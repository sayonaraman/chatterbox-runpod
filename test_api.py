"""
Test script for Chatterbox TTS RunPod API
"""

import requests
import base64
import json
import time
from pathlib import Path

def test_local_api():
    """Test the local Docker API"""
    
    base_url = "http://localhost:8000"
    
    # Test cases
    test_cases = [
        {
            "name": "English TTS",
            "payload": {
                "input": {
                    "text": "Hello world! This is a test of Chatterbox TTS running locally.",
                    "model_type": "english"
                }
            }
        },
        {
            "name": "Russian TTS", 
            "payload": {
                "input": {
                    "text": "Привет мир! Это тест Chatterbox TTS на русском языке.",
                    "model_type": "multilingual",
                    "language_id": "ru"
                }
            }
        },
        {
            "name": "Chinese TTS",
            "payload": {
                "input": {
                    "text": "你好世界！这是中文语音合成测试。",
                    "model_type": "multilingual", 
                    "language_id": "zh"
                }
            }
        },
        {
            "name": "Expressive English",
            "payload": {
                "input": {
                    "text": "This is a very exciting and dramatic announcement!",
                    "model_type": "english",
                    "exaggeration": 0.8,
                    "cfg_weight": 0.3
                }
            }
        }
    ]
    
    # Create output directory
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    
    print("🧪 Testing Chatterbox TTS API locally...")
    print(f"📁 Output directory: {output_dir.absolute()}")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        
        try:
            # Send request
            start_time = time.time()
            response = requests.post(
                f"{base_url}/run",
                json=test_case["payload"],
                timeout=60
            )
            end_time = time.time()
            
            if response.status_code == 200:
                result = response.json()
                
                if "output" in result and "audio" in result["output"]:
                    # Save audio file
                    audio_data = base64.b64decode(result["output"]["audio"])
                    filename = f"test_{i}_{test_case['name'].lower().replace(' ', '_')}.wav"
                    filepath = output_dir / filename
                    
                    with open(filepath, "wb") as f:
                        f.write(audio_data)
                    
                    duration = result["output"].get("duration", 0)
                    sample_rate = result["output"].get("sample_rate", 22050)
                    
                    print(f"   ✅ Success! Duration: {duration:.2f}s, SR: {sample_rate}Hz")
                    print(f"   💾 Saved: {filepath}")
                    print(f"   ⏱️  Processing time: {end_time - start_time:.2f}s")
                    
                elif "error" in result:
                    print(f"   ❌ API Error: {result['error']}")
                else:
                    print(f"   ❌ Unexpected response format: {result}")
                    
            else:
                print(f"   ❌ HTTP Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout after 60 seconds")
        except requests.exceptions.ConnectionError:
            print(f"   🔌 Connection error - is the server running?")
        except Exception as e:
            print(f"   💥 Unexpected error: {str(e)}")
    
    print(f"\n🏁 Testing completed! Check {output_dir} for generated audio files.")

def test_runpod_api(endpoint_id: str, api_key: str):
    """Test the RunPod Serverless API"""
    
    import runpod
    
    runpod.api_key = api_key
    endpoint = runpod.Endpoint(endpoint_id)
    
    print(f"🚀 Testing RunPod Endpoint: {endpoint_id}")
    
    # Simple test
    try:
        response = endpoint.run({
            "text": "Hello from RunPod! This is Chatterbox TTS.",
            "model_type": "english"
        })
        
        if "audio" in response:
            print("✅ RunPod API working correctly!")
            
            # Save test file
            audio_data = base64.b64decode(response["audio"])
            with open("runpod_test.wav", "wb") as f:
                f.write(audio_data)
            print("💾 Test audio saved as runpod_test.wav")
        else:
            print(f"❌ Error: {response}")
            
    except Exception as e:
        print(f"💥 RunPod API Error: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Chatterbox TTS API")
    parser.add_argument("--mode", choices=["local", "runpod"], default="local",
                       help="Test mode: local Docker or RunPod Serverless")
    parser.add_argument("--endpoint-id", help="RunPod endpoint ID (for runpod mode)")
    parser.add_argument("--api-key", help="RunPod API key (for runpod mode)")
    
    args = parser.parse_args()
    
    if args.mode == "local":
        test_local_api()
    elif args.mode == "runpod":
        if not args.endpoint_id or not args.api_key:
            print("❌ RunPod mode requires --endpoint-id and --api-key")
            exit(1)
        test_runpod_api(args.endpoint_id, args.api_key)
