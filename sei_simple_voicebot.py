import logging
import pickle

import asyncio
from livekit import api
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, openai, silero, cartesia

from handle_faq import search_faq

logger = logging.getLogger("rag-assistant")
# livekit_api = api.LiveKitAPI()


async def entrypoint(ctx: JobContext):
    livekit_api = api.LiveKitAPI()
    async def _enrich_with_rag(agent: VoicePipelineAgent, chat_ctx: llm.ChatContext):
        # locate the last user message and use it to query the RAG model
        # to get the most relevant paragraph
        # then provide that as additional context to the LLM
        user_msg = chat_ctx.messages[-1]
        documents = await search_faq(user_msg.content)

        if documents and documents["document"]:
            logger.info(f"Enriching with context: {documents['document']}")
            logger.debug(f"Enriching with context: {documents['document']}")
            rag_msg = llm.ChatMessage.create(
                text="Context:\n" + documents["document"],
                role="assistant",
            )
            # Replace last message with RAG, and append user message at the end
            chat_ctx.messages[-1] = rag_msg
            chat_ctx.messages.append(user_msg)
        else:
            logger.info("No Document Found")
            logger.debug("No Document Found")
            await agent.say("I'm sorry, I can only help with Wise transactions and payments. I don't have an answer for that. Please hold on while we transfer you to Human Agent.", allow_interruptions=False)
            await asyncio.sleep(9)
            await agent.aclose()
            # await ctx.room.disconnect()
            await livekit_api.room.delete_room(api.DeleteRoomRequest(
                room=ctx.job.room.name,
            ))

    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant specializing in Wise financial transactions. Your interface with users will be voice. "
            "Your primary goal is to provide accurate, concise, and clear answers to user inquiries regarding Wise transfers, payment processing, and banking references."
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation."
            "Use the provided context to answer the user's question if needed."
        ),
    )

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    agent = VoicePipelineAgent(
        chat_ctx=initial_ctx,
        vad=silero.VAD.load(),
        stt=deepgram.STT(),
        llm=openai.LLM(),
        tts=cartesia.TTS(),
        before_llm_cb=_enrich_with_rag,
    )

    agent.start(ctx.room)

    await agent.say("Hey, how can I help you today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))