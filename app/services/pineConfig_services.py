from config.pineCone import pc
import json
import uuid

index_name = "coderX"
index = pc.Index(index_name)


def insertPrompt_and_Payload(user_prompt:str,payload:dict)->bool:

    try:

        payload_json = json.dumps(payload)
        prompt_id = f"prompt_{uuid.uuid4().hex[:12]}"

        index.upsert_records(
            namespace="coding_Prompts",
            records=[{
                "_id" : prompt_id,
                "prompt_text": user_prompt,
                "payload_json":payload_json
            }]
        )

        print(f"[ PINECONE SUCCESS ] -> USER_PROMPT : {user_prompt} with record_id : {prompt_id}")
        return True
    except:
        print(f"[ PINECONE FAILED ] -> USER_PROMPT : {user_prompt} with record_id : {prompt_id}")
        return False

