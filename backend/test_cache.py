import requests
import time

# Define the URL and the data for the request
url = 'http://localhost:8000/query/'
data = {
    'question': 'Top 5 artists of USA',
}

# Make the first request and measure the time it takes
start_time = time.time()
response1 = requests.post(url, json=data)
end_time = time.time()
print(f"First request took {end_time - start_time} seconds")

# Make the second request and measure the time it takes
start_time = time.time()
response2 = requests.post(url, json=data)
end_time = time.time()
print(f"Second request took {end_time - start_time} seconds")

print(response1.json()==response2.json())
    
insights = insights.replace("<|im_end|>","")
