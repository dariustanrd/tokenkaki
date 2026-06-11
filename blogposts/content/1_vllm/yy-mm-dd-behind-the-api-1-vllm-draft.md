intro

running on a 4 x A100 machine, but only selecting a single A100 for this post. we'll experiment with multiple GPUs soon.

run the command `[10 Jun 10:57 AM] ~/../deploy/vllm ❯ VLLM_HOST=172.17.0.1 ./run-openai-server.sh`

then
```bash
Starting external vLLM OpenAI server
  model: Qwen/Qwen3-8B
  served model name: Qwen/Qwen3-8B
  bind: 172.17.0.1:8001
  runner: uv run
  cuda device order: PCI_BUS_ID
  cuda visible devices: 4
  uv torch backend: cu118
  extra args: <none>
INFO 06-10 10:57:29 [__init__.py:244] Automatically detected platform cuda.
INFO 06-10 10:57:31 [api_server.py:1395] vLLM API server version 0.9.2
INFO 06-10 10:57:31 [cli_args.py:325] non-default args: {'host': '172.17.0.1', 'port': 8001, 'model': 'Qwen/Qwen3-8B', 'served_model_name': ['Qwen/Qwen3-8B']}
INFO 06-10 10:57:39 [config.py:841] This model supports multiple tasks: {'reward', 'generate', 'embed', 'classify'}. Defaulting to 'generate'.
INFO 06-10 10:57:39 [config.py:1472] Using max model len 40960
INFO 06-10 10:57:39 [config.py:2285] Chunked prefill is enabled with max_num_batched_tokens=2048.
INFO 06-10 10:57:44 [__init__.py:244] Automatically detected platform cuda.
INFO 06-10 10:57:46 [core.py:526] Waiting for init message from front-end.
INFO 06-10 10:57:46 [core.py:69] Initializing a V1 LLM engine (v0.9.2) with config: model='Qwen/Qwen3-8B', speculative_config=None, tokenizer='Qwen/Qwen3-8B', skip_tokenizer_init=False, tokenizer_mode=auto, revision=None, override_neuron_config={}, tokenizer_revision=None, trust_remote_code=False, dtype=torch.bfloat16, max_seq_len=40960, download_dir=None, load_format=LoadFormat.AUTO, tensor_parallel_size=1, pipeline_parallel_size=1, disable_custom_all_reduce=False, quantization=None, enforce_eager=False, kv_cache_dtype=auto,  device_config=cuda, decoding_config=DecodingConfig(backend='auto', disable_fallback=False, disable_any_whitespace=False, disable_additional_properties=False, reasoning_backend=''), observability_config=ObservabilityConfig(show_hidden_metrics_for_version=None, otlp_traces_endpoint=None, collect_detailed_traces=None), seed=0, served_model_name=Qwen/Qwen3-8B, num_scheduler_steps=1, multi_step_stream_outputs=True, enable_prefix_caching=True, chunked_prefill_enabled=True, use_async_output_proc=True, pooler_config=None, compilation_config={"level":3,"debug_dump_path":"","cache_dir":"","backend":"","custom_ops":[],"splitting_ops":["vllm.unified_attention","vllm.unified_attention_with_output"],"use_inductor":true,"compile_sizes":[],"inductor_compile_config":{"enable_auto_functionalized_v2":false},"inductor_passes":{},"use_cudagraph":true,"cudagraph_num_of_warmups":1,"cudagraph_capture_sizes":[512,504,496,488,480,472,464,456,448,440,432,424,416,408,400,392,384,376,368,360,352,344,336,328,320,312,304,296,288,280,272,264,256,248,240,232,224,216,208,200,192,184,176,168,160,152,144,136,128,120,112,104,96,88,80,72,64,56,48,40,32,24,16,8,4,2,1],"cudagraph_copy_inputs":false,"full_cuda_graph":false,"max_capture_size":512,"local_cache_dir":null}
INFO 06-10 10:57:52 [parallel_state.py:1076] rank 0 in world size 1 is assigned as DP rank 0, PP rank 0, TP rank 0, EP rank 0
WARNING 06-10 10:57:52 [topk_topp_sampler.py:59] FlashInfer is not available. Falling back to the PyTorch-native implementation of top-p & top-k sampling. For the best performance, please install FlashInfer.
INFO 06-10 10:57:52 [gpu_model_runner.py:1770] Starting to load model Qwen/Qwen3-8B...
INFO 06-10 10:57:53 [gpu_model_runner.py:1775] Loading model from scratch...
INFO 06-10 10:57:53 [cuda.py:284] Using Flash Attention backend on V1 engine.
INFO 06-10 10:57:53 [weight_utils.py:292] Using model weights format ['*.safetensors']
Loading safetensors checkpoint shards:   0% Completed | 0/5 [00:00<?, ?it/s]
Loading safetensors checkpoint shards:  20% Completed | 1/5 [00:00<00:01,  2.06it/s]
Loading safetensors checkpoint shards:  40% Completed | 2/5 [00:00<00:01,  2.87it/s]
Loading safetensors checkpoint shards:  60% Completed | 3/5 [00:01<00:00,  2.74it/s]
Loading safetensors checkpoint shards:  80% Completed | 4/5 [00:01<00:00,  2.42it/s]
Loading safetensors checkpoint shards: 100% Completed | 5/5 [00:02<00:00,  2.22it/s]
Loading safetensors checkpoint shards: 100% Completed | 5/5 [00:02<00:00,  2.35it/s]

INFO 06-10 10:57:56 [default_loader.py:272] Loading weights took 2.22 seconds
INFO 06-10 10:57:57 [gpu_model_runner.py:1801] Model loading took 15.2683 GiB and 3.617503 seconds
INFO 06-10 10:58:04 [backends.py:508] Using cache directory: /home/darius/.cache/vllm/torch_compile_cache/361dd3f364/rank_0_0/backbone for vLLM's torch.compile
INFO 06-10 10:58:04 [backends.py:519] Dynamo bytecode transform time: 7.41 s
INFO 06-10 10:58:11 [backends.py:155] Directly load the compiled graph(s) for shape None from the cache, took 6.425 s
INFO 06-10 10:58:13 [monitor.py:34] torch.compile takes 7.41 s in total
INFO 06-10 10:58:13 [gpu_worker.py:232] Available KV cache memory: 18.69 GiB
INFO 06-10 10:58:14 [kv_cache_utils.py:716] GPU KV cache size: 136,080 tokens
INFO 06-10 10:58:14 [kv_cache_utils.py:720] Maximum concurrency for 40,960 tokens per request: 3.32x
Capturing CUDA graph shapes: 100%|██████████████████████████████████████████████| 67/67 [00:23<00:00,  2.88it/s]
INFO 06-10 10:58:37 [gpu_model_runner.py:2326] Graph capturing finished in 23 secs, took 2.24 GiB
INFO 06-10 10:58:37 [core.py:172] init engine (profile, create kv cache, warmup model) took 40.37 seconds
INFO 06-10 10:58:38 [loggers.py:137] Engine 000: vllm cache_config_info with initialization after num_gpu_blocks is: 8505
WARNING 06-10 10:58:38 [config.py:1392] Default sampling parameters have been overridden by the model's Hugging Face generation config recommended from the model creator. If this is not intended, please relaunch vLLM instance with `--generation-config vllm`.
INFO 06-10 10:58:38 [serving_chat.py:125] Using default chat sampling params from model: {'temperature': 0.6, 'top_k': 20, 'top_p': 0.95}
INFO 06-10 10:58:38 [serving_completion.py:72] Using default completion sampling params from model: {'temperature': 0.6, 'top_k': 20, 'top_p': 0.95}
INFO 06-10 10:58:38 [api_server.py:1457] Starting vLLM API server 0 on http://172.17.0.1:8001
INFO 06-10 10:58:38 [launcher.py:29] Available routes are:
INFO 06-10 10:58:38 [launcher.py:37] Route: /openapi.json, Methods: GET, HEAD
INFO 06-10 10:58:38 [launcher.py:37] Route: /docs, Methods: GET, HEAD
INFO 06-10 10:58:38 [launcher.py:37] Route: /docs/oauth2-redirect, Methods: GET, HEAD
INFO 06-10 10:58:38 [launcher.py:37] Route: /redoc, Methods: GET, HEAD
INFO 06-10 10:58:38 [launcher.py:37] Route: /health, Methods: GET
INFO 06-10 10:58:38 [launcher.py:37] Route: /load, Methods: GET
INFO 06-10 10:58:38 [launcher.py:37] Route: /ping, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /ping, Methods: GET
INFO 06-10 10:58:38 [launcher.py:37] Route: /tokenize, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /detokenize, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /v1/models, Methods: GET
INFO 06-10 10:58:38 [launcher.py:37] Route: /version, Methods: GET
INFO 06-10 10:58:38 [launcher.py:37] Route: /v1/chat/completions, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /v1/completions, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /v1/embeddings, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /pooling, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /classify, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /score, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /v1/score, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /v1/audio/transcriptions, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /v1/audio/translations, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /rerank, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /v1/rerank, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /v2/rerank, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /invocations, Methods: POST
INFO 06-10 10:58:38 [launcher.py:37] Route: /metrics, Methods: GET
INFO:     Started server process [45560]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

then can see GPU allocated

```bash
[10 Jun 10:58 AM] ~/../deploy/compose ❯ nvidia-smi
Mon Jun  10 10:58:59 2026       
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 535.247.01             Driver Version: 535.247.01   CUDA Version: 12.2     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA A100-SXM4-40GB          On  | 00000000:01:00.0 Off |                    0 |
| N/A   32C    P0              56W / 275W |      0MiB / 40960MiB |      0%      Default |
|                                         |                      |             Disabled |
+-----------------------------------------+----------------------+----------------------+
|   1  NVIDIA A100-SXM4-40GB          On  | 00000000:47:00.0 Off |                    0 |
| N/A   32C    P0              54W / 275W |      0MiB / 40960MiB |      0%      Default |
|                                         |                      |             Disabled |
+-----------------------------------------+----------------------+----------------------+
|   2  NVIDIA A100-SXM4-40GB          On  | 00000000:81:00.0 Off |                    0 |
| N/A   32C    P0              55W / 275W |      0MiB / 40960MiB |      0%      Default |
|                                         |                      |             Disabled |
+-----------------------------------------+----------------------+----------------------+
|   3  NVIDIA DGX Display             On  | 00000000:C1:00.0 Off |                  N/A |
| 33%   32C    P8              N/A /  50W |      1MiB /  4096MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
|   4  NVIDIA A100-SXM4-40GB          On  | 00000000:C2:00.0 Off |                    0 |
| N/A   32C    P0              56W / 275W |  39062MiB / 40960MiB |      0%      Default |
|                                         |                      |             Disabled |
+-----------------------------------------+----------------------+----------------------+
                                                                                         
+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
|    4   N/A  N/A   2194728      C   ...nkaki/deploy/vllm/.venv/bin/python3    39052MiB |
+---------------------------------------------------------------------------------------+
```

lets dive abit deeper into the startup logs, because at this stage it is already interesting.

1. VRAM is preallocated at this point already

How is this done, where does the memory go towards?

  1. From `vllm/v1/worker/gpu_worker.py`, it takes a memory snapshot and computes allowed budget based on `cache_config.gpu_memory_utilization` which defaults to `0.9`. 
    This implies `~40 GiB * 0.9 = ~36 GiB requested budget`.
  2. Model weights are loaded. For Qwen3-8B at BF16, approx 16GB in model size from HF, and we can see in the logs `Model loading took 15.2683 GiB and 3.617503 seconds` which is expected.
  3. Estimate the overhead for non-KV memory (e.g activations, other buffers and overhead) via profiling as per `vllm/v1/worker/gpu_worker.py` with `memory_profiling()`.
    This results in `available_kv_cache_memory = self.requested_memory - profile_result.non_kv_cache_memory`, which is logged as `Available KV cache memory: 18.69 GiB`.
    How this breaks down to the actual model:
      For Qwen3-8B, from config.json:
      ```json
        num_hidden_layers = 36
        num_key_value_heads = 8
        head_dim = 128
        torch_dtype = bfloat16
      ```
      We can calculate the per-layer KV cache size (see `vllm/v1/kv_cache_interface.py`): `2 * block_size * num_kv_heads * head_size * get_dtype_size(dtype)`
      
      For 1 token in the block, per-token per-layer KV cache size for our model is: `2 * 1 * 8 * 128 * 2 = 4,096 bytes`
      Then across all layers in the model: `4,096 * 36 = 147,456 bytes`

      Then now per-block, with block size 16: `147,456 * 16 = 2,359,296 bytes`. Means that 1 block requires a total of `2.359296 MB = 2.25 MiB`. (base 10 vs base 2 units!)

      Wwe also know that our maximum model input context length is 40960 tokens, as seen in `INFO 06-10 10:57:39 [config.py:1472] Using max model len 40960`.

      So at maximum length, we will need `147,456 bytes/tok * 40960 toks = 6,039,797,760 bytes = 6.03979776 GB = 5.625 GiB` for the full model KV cache.

      Given our available KV cache memory of 18.69 GiB, this means:
      - we have max number of blocks as `18.69 GiB total memory remaining / 2.25 MiB KV size per block = 8,506 blocks`, which when using raw byte values to compute it is in actual fact 8505 blocks, and then `8505 blocks * 16 tokens/block = 136,080 token slots` which matches our logs, and
      - we can fit at most `18.69/5.625 = 3.32267` concurrent full requests at the same time (i.e. maximum concurrency), which also matches our logs of 3.32x max concurrency (but we must also note that this max concurrency is theoretical, actual concurrency depends on prompts used and generation lengths).

Thus at the end our total usage = ~39GB, with breakdown as per:
```text
- A100 budget at 90%             ~36 GiB
  - model weights                  ~15.27 GiB
  - other profiled non-KV memory   (whatever remains before KV sizing)
  - KV cache pool                  18.69 GiB
- CUDA graph capture             +2.24 GiB after KV allocation
```

2. Some optimizations are already enabled by default.

TODO: look into the logs more here.

another thing we can notice at this point is that cold start time is quite long, mainly because of this step: 

```bash
Capturing CUDA graph shapes: 100%|██████████████████████████████████████████████| 67/67 [00:23<00:00,  2.88it/s]
INFO 06-10 10:58:37 [gpu_model_runner.py:2326] Graph capturing finished in 23 secs, took 2.24 GiB
```

this can be improved later using checkpointing?

at this point we can test that the vllm endpoint is available, and we can run some initial tests to see if we can run inference

```bash
[10 Jun 10:59 AM] ~/Workspaces/tokenkaki ❯ VLLM_HOST=172.17.0.1 ./deploy/vllm/smoke-openai.sh
Checking vLLM models endpoint at http://172.17.0.1:8001/v1/models
{"object":"list","data":[{"id":"Qwen/Qwen3-8B","object":"model","created":1781060392,"owned_by":"vllm","root":"Qwen/Qwen3-8B","parent":null,"max_model_len":40960,"permission":[{"id":"modelperm-ca6faa0df97343cd9dae6194f55488dc","object":"model_permission","created":1781060392,"allow_create_engine":false,"allow_sampling":true,"allow_logprobs":true,"allow_search_indices":false,"allow_view":true,"allow_fine_tuning":false,"organization":"*","group":null,"is_blocking":false}]}]}
Checking vLLM non-streaming chat completion for Qwen/Qwen3-8B
{"id":"chatcmpl-c5f9de61429847e7843ce02f565c0248","object":"chat.completion","created":1781060394,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"message":{"role":"assistant","reasoning_content":null,"content":"<think>\nOkay, the user wants me to reply with exactly \"tokenkaki-vllm-smoke-ok\". Let me check if there's any hidden request here. The phrase seems like a specific identifier or a test string. Maybe they're verifying if I can follow instructions precisely. I should make sure not to add any extra text. Just the exact string they provided. Alright, I'll respond with that.\n</think>\n\ntokenkaki-vllm-smoke-ok","tool_calls":[]},"logprobs":null,"finish_reason":"stop","stop_reason":null}],"usage":{"prompt_tokens":21,"total_tokens":116,"completion_tokens":95,"prompt_tokens_details":null},"prompt_logprobs":null,"kv_transfer_params":null}
```

and now on the server side we can see
```bash
INFO:     10.97.176.105:49022 - "GET /v1/models HTTP/1.1" 200 OK
INFO 06-10 10:59:54 [chat_utils.py:444] Detected the chat template content format to be 'string'. You can set `--chat-template-content-format` to override this.
INFO 06-10 10:59:54 [logger.py:43] Received request chatcmpl-c5f9de61429847e7843ce02f565c0248: prompt: '<|im_start|>user\nReply with exactly: tokenkaki-vllm-smoke-ok<|im_end|>\n<|im_start|>assistant\n', params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.0, top_p=1.0, top_k=0, min_p=0.0, seed=None, stop=[], stop_token_ids=[], bad_words=[], include_stop_str_in_output=False, ignore_eos=False, max_tokens=128, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, truncate_prompt_tokens=None, guided_decoding=None, extra_args=None), prompt_token_ids: None, prompt_embeds shape: None, lora_request: None, prompt_adapter_request: None.
INFO 06-10 10:59:54 [async_llm.py:270] Added request chatcmpl-c5f9de61429847e7843ce02f565c0248.
INFO:     10.97.176.105:49024 - "POST /v1/chat/completions HTTP/1.1" 200 OK
INFO 06-10 10:59:59 [loggers.py:118] Engine 000: Avg prompt throughput: 2.1 tokens/s, Avg generation throughput: 9.5 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 0.0%
INFO 06-10 11:00:09 [loggers.py:118] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 0.0 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 0.0%
```

congrats! model is served. we are done, and can now close shop lol. okay its not so simple.

lets try running it again identically, without restarting the server.

```bash
Checking vLLM models endpoint at http://172.17.0.1:8001/v1/models
{"object":"list","data":[{"id":"Qwen/Qwen3-8B","object":"model","created":1781060549,"owned_by":"vllm","root":"Qwen/Qwen3-8B","parent":null,"max_model_len":40960,"permission":[{"id":"modelperm-475e8dddc023494e9d418e2b6dd01b2c","object":"model_permission","created":1781060549,"allow_create_engine":false,"allow_sampling":true,"allow_logprobs":true,"allow_search_indices":false,"allow_view":true,"allow_fine_tuning":false,"organization":"*","group":null,"is_blocking":false}]}]}
Checking vLLM non-streaming chat completion for Qwen/Qwen3-8B
{"id":"chatcmpl-b4c2e938c6684b449db1954e898439ee","object":"chat.completion","created":1781060549,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"message":{"role":"assistant","reasoning_content":null,"content":"<think>\nOkay, the user wants me to reply with exactly \"tokenkaki-vllm-smoke-ok\". Let me check if there's any hidden request here. The phrase seems like a specific identifier or a test string. Maybe they're verifying if I can follow instructions precisely. I should make sure not to add any extra text. Just the exact string they provided. Alright, I'll respond with that.\n</think>\n\ntokenkaki-vllm-smoke-ok","tool_calls":[]},"logprobs":null,"finish_reason":"stop","stop_reason":null}],"usage":{"prompt_tokens":21,"total_tokens":116,"completion_tokens":95,"prompt_tokens_details":null},"prompt_logprobs":null,"kv_transfer_params":null}
```

```bash
INFO:     10.97.176.105:53836 - "GET /v1/models HTTP/1.1" 200 OK
INFO 06-10 11:02:29 [logger.py:43] Received request chatcmpl-b4c2e938c6684b449db1954e898439ee: prompt: '<|im_start|>user\nReply with exactly: tokenkaki-vllm-smoke-ok<|im_end|>\n<|im_start|>assistant\n', params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.0, top_p=1.0, top_k=0, min_p=0.0, seed=None, stop=[], stop_token_ids=[], bad_words=[], include_stop_str_in_output=False, ignore_eos=False, max_tokens=128, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, truncate_prompt_tokens=None, guided_decoding=None, extra_args=None), prompt_token_ids: None, prompt_embeds shape: None, lora_request: None, prompt_adapter_request: None.
INFO 06-10 11:02:29 [async_llm.py:270] Added request chatcmpl-b4c2e938c6684b449db1954e898439ee.
INFO 06-10 11:02:29 [loggers.py:118] Engine 000: Avg prompt throughput: 2.1 tokens/s, Avg generation throughput: 0.4 tokens/s, Running: 1 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 38.1%
INFO:     10.97.176.105:53840 - "POST /v1/chat/completions HTTP/1.1" 200 OK
```

something interesting to note in this quick run is that we can already see optimizations happening under the hood in vLLM from these logs. spot it?

its `Prefix cache hit rate: 38.1%`! we are using prefix caching already by default in vLLM. 
What does this mean?

TODO: explain [prefix caching](https://bentoml.com/llm/inference-optimization/prefix-caching)

So by theory since the request is identical, shouldnt the full prompt be cached?

In practice how is this number calculated in vLLM?

[Prefix Caching](https://docs.vllm.ai/en/v0.9.2/design/v1/prefix_caching.html)

from `vllm/v1/metrics/stats.py`,

```python
@dataclass
class PrefixCacheStats:
    """Stores prefix cache hit statistics."""
    # Whether reset_prefix_cache was invoked.
    reset: bool = False
    # The number of requests in this update.
    requests: int = 0
    # The number of queries in these requests. Note that "queries" here
    # means the number of tokens that were queried from the cache.
    queries: int = 0
    # The number of hits in these requests.
    hits: int = 0
```

and in `vllm/v1/core/kv_cache_manager.py`, queries += request.num_tokens, hits += num_new_computed_tokens, where the caching is done by full KV blocks, not arbitrary number of token lengths.

```python
def get_computed_blocks(...):

  ...

  if self.log_stats:
    assert self.prefix_cache_stats is not None
    self.prefix_cache_stats.requests += 1
  
  ...

  if self.log_stats:
    assert self.prefix_cache_stats is not None
    self.prefix_cache_stats.queries += request.num_tokens
    self.prefix_cache_stats.hits += num_new_computed_tokens
```

then from `vllm/v1/core/kv_cache_utils.py`, the requests are aggregated, and finally get the hit rate as aggregated_query_hit / aggregated_query_total.

```python
class PrefixCachingMetrics:
    """Metrics for prefix caching with a hit rate of the max recent N requests.

    Args:
        max_recent_requests: The number of the max recent requests to aggregate.
            Defaults to 1000.
    """
    
    ...

    def observe(self, stats: PrefixCacheStats):
      """Observe the prefix caching for a set of requests.

      This function is called with information gathered when new requests
      are being scheduled and are looking for computed blocks.

      When there are more than `interval` requests, the oldest set of
      requests are removed from the metrics.

      Args:
          stats: The prefix cache stats.
      """
      # reset_prefix_cache was invoked before the current update.
      # Reset the metrics before aggregating the current stats.
      if stats.reset:
          self.reset()

      # Update the metrics.
      self.query_queue.append((stats.requests, stats.queries, stats.hits))
      self.aggregated_requests += stats.requests
      self.aggregated_query_total += stats.queries
      self.aggregated_query_hit += stats.hits

      # Remove the oldest stats if the number of requests exceeds.
      if self.aggregated_requests > self.max_recent_requests:
          old_requests, old_queries, old_hits = self.query_queue.popleft()
          self.aggregated_requests -= old_requests
          self.aggregated_query_total -= old_queries
          self.aggregated_query_hit -= old_hits
    
    ...

    @property
    def hit_rate(self) -> float:
        """Calculate the hit rate for the past N requests."""
        if self.aggregated_query_total == 0:
            return 0.0
        return self.aggregated_query_hit / self.aggregated_query_total
```

so what happens when we run one more time?

```bash
INFO:     10.97.176.105:48428 - "GET /v1/models HTTP/1.1" 200 OK
INFO 06-10 11:04:46 [logger.py:43] Received request chatcmpl-fd06461a78ae4310b3c3dee576eabb87: prompt: '<|im_start|>user\nReply with exactly: tokenkaki-vllm-smoke-ok<|im_end|>\n<|im_start|>assistant\n', params: SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.0, top_p=1.0, top_k=0, min_p=0.0, seed=None, stop=[], stop_token_ids=[], bad_words=[], include_stop_str_in_output=False, ignore_eos=False, max_tokens=128, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, truncate_prompt_tokens=None, guided_decoding=None, extra_args=None), prompt_token_ids: None, prompt_embeds shape: None, lora_request: None, prompt_adapter_request: None.
INFO 06-10 11:04:46 [async_llm.py:270] Added request chatcmpl-fd06461a78ae4310b3c3dee576eabb87.
INFO:     10.97.176.105:48440 - "POST /v1/chat/completions HTTP/1.1" 200 OK
INFO 06-10 11:04:49 [loggers.py:118] Engine 000: Avg prompt throughput: 2.1 tokens/s, Avg generation throughput: 9.5 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 50.8%
```

`Prefix cache hit rate: 50.8%`

therefore in practice what prefix caching looks like in vLLM which led to these values is the following:

In 1 smoke request, we have `prompt_tokens = 21`, and we know that default vLLM CUDA `block_size = 16`. Since vLLM prefix caching works in full KV blocks, not arbitrary token spans, with the default CUDA block size of 16, the 21-token prompt becomes:

```text
block 1: tokens 1-16   full block, cacheable
block 2: tokens 17-21  partial block, not cacheable
```

so per run:
```text
Run 1:
hits = 0
queries = 21
hit rate = 0 / 21 = 0.0%

Run 2: 
hits = 16
queries = 21

aggregate hits = 0 + 16 = 16
aggregate queries = 21 + 21 = 42

aggregate hit rate = 16 / 42 = 0.38095 = 38.1%

Run 3:
hits = 16
queries = 21

aggregate hits = 0 + 16 + 16 = 32
aggregate queries = 21 + 21 + 21 = 63

aggregate hit rate = 32 / 63 = 0.5079 = 50.8%
```

next, why is `GPU KV cache usage: 0.0%`? how are the requests related to KV cache usage? shouldnt kv cache already been built from previous request, and now appending for subsequent request? 

TODO: explanation here

so if we increase the length of prompt, we should see an increase in this value right?
```python
import json
import urllib.request

host = "172.17.0.1"
port = 8001
model = "Qwen/Qwen3-8B"

prompt = (
    "You are validating vLLM KV cache occupancy. "
    "Repeat this workload context carefully. "
    + ("tokenkaki kv-cache validation paragraph. " * 4500)
)

body = {
    "model": model,
    "messages": [{"role": "user", "content": prompt}],
    "temperature": 0,
    "max_tokens": 2048,
    "stream": False,
}

req = urllib.request.Request(
    f"http://{host}:{port}/v1/chat/completions",
    data=json.dumps(body).encode(),
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(req, timeout=600) as resp:
    data = json.loads(resp.read())
    print(json.dumps(data["usage"], indent=2))
```

response logs on the server:

```bash
INFO 06-10 14:33:57 [async_llm.py:270] Added request chatcmpl-58d926c7e6a64e92b4718e3b9f16e58d.
INFO 06-10 14:34:03 [loggers.py:118] Engine 000: Avg prompt throughput: 3602.4 tokens/s, Avg generation throughput: 2.8 tokens/s, Running: 1 reqs, Waiting: 0 reqs, GPU KV cache usage: 26.5%, Prefix cache hit rate: 0.0%
INFO 06-10 14:34:13 [loggers.py:118] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 55.2 tokens/s, Running: 1 reqs, Waiting: 0 reqs, GPU KV cache usage: 26.9%, Prefix cache hit rate: 0.0%
INFO 06-10 14:34:23 [loggers.py:118] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 54.8 tokens/s, Running: 1 reqs, Waiting: 0 reqs, GPU KV cache usage: 27.3%, Prefix cache hit rate: 0.0%
INFO:     10.97.176.105:35478 - "POST /v1/chat/completions HTTP/1.1" 200 OK
INFO 06-10 14:34:33 [loggers.py:118] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 39.1 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 0.0%
INFO 06-10 14:34:43 [loggers.py:118] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 0.0 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 0.0%
```

response from the server:
```json
{
  "prompt_tokens": 36025,
  "total_tokens": 37544,
  "completion_tokens": 1519,
  "prompt_tokens_details": null
}
```

therefore this is coherent, because given block_size 16 and the prefill phase taking the full input prompt length:
```text
ceil(36,025 / 16) = 2,252 blocks
2,252 / 8,505 = 26.48%
```
where 8505 is from the startup logs where we previously calculated to be the maximum number of blocks allowed on our hardware due to VRAM size.

then, as the generation continues into the decode phase and completes decode:
```text
ceil(37,544 / 16) = 2,347 blocks
2,347 / 8,505 = 27.60%
```
which is near 27.3% from the logs. likely not exact match because of logging sampling frequency.

then after decode completes, the GPU KV cache usage gets freed and goes to 0.0%.

---

now lets run some benchmarks of vllm alone - in our plan we have 3 benchmarks to run at this stage:
vllm latency, throughput and serve.

we can stop our running server at this point, since these benchmarks will start a server on its own too, and run the benchmark there.

benchmark 1: latency

```bash
cd /home/darius/Workspaces/tokenkaki/deploy/vllm

CUDA_DEVICE_ORDER=PCI_BUS_ID \
CUDA_VISIBLE_DEVICES=4 \
UV_TORCH_BACKEND=cu118 \
uv run vllm bench latency \
  --model Qwen/Qwen3-8B \
  --batch-size 1 \
  --input-len 128 \
  --output-len 64 \
  --num-iters-warmup 10 \
  --num-iters 30 \
  --output-json ../../experiments/1_vllm_baseline_Qwen3-8B/1_latency/vllm-latency-qwen3-8b-a100.json
```


TODO: benchmarks 1 - 3

---

TODO: add motivation for having a gateway here, how we design the gateway here.

then move to starting the gateway

---

next start gateway
`~/../deploy/compose ❯ docker compose up --build`

then check running
```
~/../deploy/compose ❯ curl http://127.0.0.1:8000/healthz
{"status":"ok","request_id":"4465d0b6-671b-4932-93f5-7a1f3eef3e88"}%     

~/../deploy/compose ❯ curl http://127.0.0.1:8000/v1/models
{"object":"list","data":[{"id":"qwen3-8b","object":"model","created":0,"owned_by":"tokenkaki"}]}

~/../deploy/compose ❯ curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -H 'x-request-id: compose-chat-001' \
  -d '{
    "model": "qwen3-8b",
    "messages": [
      {"role": "user", "content": "Say hello in one short sentence."}
    ],
    "temperature": 0,
    "max_tokens": 64,
    "chat_template_kwargs": {"enable_thinking": false}
  }'
{"id":"chatcmpl-compose-chat-001","object":"chat.completion","created":1780929861,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"message":{"role":"assistant","reasoning_content":null,"content":"Hello! How can I assist you today?","tool_calls":[]},"logprobs":null,"finish_reason":"stop","stop_reason":null}],"usage":{"prompt_tokens":19,"total_tokens":29,"completion_tokens":10,"prompt_tokens_details":null},"prompt_logprobs":null,"kv_transfer_params":null}

~/../deploy/compose ❯ curl http://127.0.0.1:8000/v1/chat/completions \
  -H 'content-type: application/json' \
  -H 'x-request-id: compose-chat-001' \
  -d '{
    "model": "qwen3-8b", "stream":"true",
    "messages": [
      {"role": "user", "content": "Say hello in one short sentence."}
    ],
    "temperature": 0,
    "max_tokens": 64,
    "chat_template_kwargs": {"enable_thinking": false}
  }'
data: {"id":"chatcmpl-compose-chat-001","object":"chat.completion.chunk","created":1780929974,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"delta":{"role":"assistant","content":""},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-compose-chat-001","object":"chat.completion.chunk","created":1780929974,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"delta":{"content":"Hello"},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-compose-chat-001","object":"chat.completion.chunk","created":1780929974,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"delta":{"content":"!"},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-compose-chat-001","object":"chat.completion.chunk","created":1780929974,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"delta":{"content":" How"},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-compose-chat-001","object":"chat.completion.chunk","created":1780929974,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"delta":{"content":" can"},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-compose-chat-001","object":"chat.completion.chunk","created":1780929974,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"delta":{"content":" I"},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-compose-chat-001","object":"chat.completion.chunk","created":1780929974,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"delta":{"content":" assist"},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-compose-chat-001","object":"chat.completion.chunk","created":1780929974,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"delta":{"content":" you"},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-compose-chat-001","object":"chat.completion.chunk","created":1780929974,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"delta":{"content":" today"},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-compose-chat-001","object":"chat.completion.chunk","created":1780929974,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"delta":{"content":"?"},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-compose-chat-001","object":"chat.completion.chunk","created":1780929974,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"delta":{"content":""},"logprobs":null,"finish_reason":"stop","stop_reason":null}]}

data: [DONE]
```

---

okay now the full baseline system is up and running.

we can run our last benchmark step 4 - vllm serve for the whole gateway + vllm

---
TODO: benchmark

---

TODO: analysis of benchmark diffs.

---

TODO: how this leads to milestone 2 / next post
