from llama_cpp import Llama
from datetime import datetime
llm = Llama.from_pretrained(
    repo_id="Qwen/Qwen1.5-0.5B-Chat-GGUF",
    filename="*q8_0.gguf",
    verbose=False
)


def get_poem(args, timecrawler):    
    for day in timecrawler:
        timestamp = datetime.strptime(day.timestamp, "%Y-%m-%d").strftime("%B %d, %Y")

        
        data_data = day.get_channel_data("death")
        weather_data = day.get_channel_data("weather")
        event_data = day.get_channel_data("event")

        prompt = f"Q: Write a poem about {timestamp}.\n"
        if data_data is not None:
            prompt += f"Include a reference to the death '{data_data['data']['name']}'.\n"
        if weather_data is not None:
            print(weather_data)
            if weather_data["data"]["snowfall"] > 0.0:
                prompt += "Include a reference to snow.\n"
        if event_data is not None:
            prompt += f"Include a reference to the event '{event_data['data']['name']}'.\n"
        prompt += "\n"
        
        print(f"Prompt: {prompt}")
        output = llm(
            prompt, 
            max_tokens=1024,
            stop=None, 
            temperature=0.85,
            echo=False,
            mirostat_mode=2
        ) 
        output = output["choices"][0]['text']
        print(f"{day.timestamp} - got poem '{output}'")
        day.update_channel("poem", [], {
            "poem" : output
        })


