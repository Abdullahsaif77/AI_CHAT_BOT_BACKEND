
import time

from fastapi import HTTPException
from sqlalchemy.orm import Session

from schema import chat as ChatSchema
from integrations.gemini import client
from models.conversation import conversation
from models.message import Message


def ChatMessage(data: ChatSchema.ChatRequest, db: Session):
    try:
        # 1. Create a conversation or fetch the existing one
        if data.conversation_id is None:
            current_conversation = conversation(
                title="My First Chat"
            )
            db.add(current_conversation)
            db.flush()

            conversation_id = current_conversation.id

        else:
            conversation_id = data.conversation_id

            current_conversation = (
                db.query(conversation)
                .filter(conversation.id == conversation_id)
                .first()
            )

            if current_conversation is None:
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found",
                )

        # 2. Fetch the previous 10 messages BEFORE adding the new message
        previous_messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(10)
            .all()
        )

        previous_messages.reverse()
        print("Conversation ID:", conversation_id)

        for message in previous_messages:
          print(f"{message.role}: {message.content}")

        # 3. Format history for Gemini
        contents = []

        for message in previous_messages:
            contents.append({
                "role": "user" if message.role == "user" else "model",
                "parts": [{"text": message.content}],
            })

        # Add the current user message to Gemini's context
        contents.append({
            "role": "user",
            "parts": [{"text": data.message}],
        })

        # 4. Save the new user message
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=data.message,
        )
        db.add(user_message)

        # 5. Ask Gemini using the conversation history
        start = time.perf_counter()

        ai_response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=contents,
            config={
                "thinking_config": {
                    "thinking_level": "LOW"
                },
                "max_output_tokens": 100,
            },
        )

        print(
            "Gemini time:",
            round(time.perf_counter() - start, 2),
            "seconds",
        )

        if not ai_response.text:
            raise HTTPException(
                status_code=503,
                detail="AI service returned an empty response.",
            )

        # 6. Save the assistant's reply
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response.text,
        )
        db.add(assistant_message)

        # 7. Commit all database changes
        db.commit()

        # 8. Return the reply and conversation ID
        return {
            "response": ai_response.text,
            "conversation_id": conversation_id,
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        print("ERROR TYPE:", type(exc).__name__)
        print("ERROR DETAILS:", str(exc))

        raise HTTPException(
            status_code=503,
            detail="Unable to process your message.",
        ) from exc
