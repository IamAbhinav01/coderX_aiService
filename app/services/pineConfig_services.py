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
    except Exception as e:
        print(f"[ PINECONE FAILED ] -> USER_PROMPT : {user_prompt} with error : {e}")
        return False


def Hit_and_Return(user_prompt:str,threshold:float = 0.88):

    try:
        response = index.search(
            namespace="coding_Prompts",
            query={
                "inputs":{"text":user_prompt},
                "top_k":1
            },
            fields=["prompt_text", "payload_json"]
            )

        if response and response.result and response.result.hits:

            top_hit = response.result.hits[0]
            similarity_score = top_hit.score

            print(f"[Pinecone search] Top Match Score : {similarity_score:.4f} for prompt: `{user_prompt}")

            if similarity_score >= threshold:
                payload_str = top_hit.fields.get("payload_json")
                if payload_str:
                    payload = json.loads(payload_str)
                    payload["_cache_hit"] = True
                    payload["_similarity"] = round(similarity_score,4)
                    return payload

        return None
    except Exception as e:
        print(f"Error occured , error : {e}")
