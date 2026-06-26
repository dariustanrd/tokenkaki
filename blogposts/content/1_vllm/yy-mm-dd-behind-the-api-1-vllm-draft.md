intro

running on a 4 x A100 machine, but only selecting a single A100 for this post. we'll experiment with multiple GPUs soon.

I pinned vLLM to `0.19.1` because my host is running NVIDIA driver `535.247.01`, which is a CUDA 12.2-era driver. Newer vLLM releases move to newer PyTorch/vLLM binary stacks, and the current prebuilt path defaults to CUDA 12.9, with CUDA 13 variants requiring driver 580+. Rather than upgrade the host driver for this first baseline, I used `0.19.1`, the newest vLLM release I validated on this machine with `UV_TORCH_BACKEND=auto`.

run the command

```bash
[25 Jun 05:21 PM] ~/../deploy/vllm ❯ VLLM_HOST=172.17.0.1 CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=4 UV_TORCH_BACKEND=auto ./run-openai-server.sh
```

then we get vLLM `0.19.1` serving Qwen3-8B on one selected A100:

```bash
Starting external vLLM OpenAI server
  model: Qwen/Qwen3-8B
  served model name: Qwen/Qwen3-8B
  bind: 172.17.0.1:8001
  runner: uv run
  cuda device order: PCI_BUS_ID
  cuda visible devices: 4
  uv torch backend: auto
  extra args: <none>
(APIServer pid=3380144) INFO 06-25 17:21:29 [utils.py:299] 
(APIServer pid=3380144) INFO 06-25 17:21:29 [utils.py:299]        █     █     █▄   ▄█
(APIServer pid=3380144) INFO 06-25 17:21:29 [utils.py:299]  ▄▄ ▄█ █     █     █ ▀▄▀ █  version 0.19.1
(APIServer pid=3380144) INFO 06-25 17:21:29 [utils.py:299]   █▄█▀ █     █     █     █  model   Qwen/Qwen3-8B
(APIServer pid=3380144) INFO 06-25 17:21:29 [utils.py:299]    ▀▀  ▀▀▀▀▀ ▀▀▀▀▀ ▀     ▀
(APIServer pid=3380144) INFO 06-25 17:21:29 [utils.py:299] 
(APIServer pid=3380144) INFO 06-25 17:21:29 [utils.py:233] non-default args: {'model_tag': 'Qwen/Qwen3-8B', 'host': '172.17.0.1', 'port': 8001, 'model': 'Qwen/Qwen3-8B', 'served_model_name': ['Qwen/Qwen3-8B']}
(APIServer pid=3380144) WARNING 06-25 17:21:29 [envs.py:1744] Unknown vLLM environment variable detected: VLLM_HOST
(APIServer pid=3380144) INFO 06-25 17:21:31 [model.py:549] Resolved architecture: Qwen3ForCausalLM
(APIServer pid=3380144) INFO 06-25 17:21:31 [model.py:1678] Using max model len 40960
(APIServer pid=3380144) INFO 06-25 17:21:31 [vllm.py:790] Asynchronous scheduling is enabled.
(EngineCore pid=3380462) INFO 06-25 17:21:40 [core.py:105] Initializing a V1 LLM engine (v0.19.1) with config: model='Qwen/Qwen3-8B', speculative_config=None, tokenizer='Qwen/Qwen3-8B', skip_tokenizer_init=False, tokenizer_mode=auto, revision=None, tokenizer_revision=None, trust_remote_code=False, dtype=torch.bfloat16, max_seq_len=40960, download_dir=None, load_format=auto, tensor_parallel_size=1, pipeline_parallel_size=1, data_parallel_size=1, decode_context_parallel_size=1, dcp_comm_backend=ag_rs, disable_custom_all_reduce=False, quantization=None, enforce_eager=False, enable_return_routed_experts=False, kv_cache_dtype=auto, device_config=cuda, structured_outputs_config=StructuredOutputsConfig(backend='auto', disable_any_whitespace=False, disable_additional_properties=False, reasoning_parser='', reasoning_parser_plugin='', enable_in_reasoning=False), observability_config=ObservabilityConfig(show_hidden_metrics_for_version=None, otlp_traces_endpoint=None, collect_detailed_traces=None, kv_cache_metrics=False, kv_cache_metrics_sample=0.01, cudagraph_metrics=False, enable_layerwise_nvtx_tracing=False, enable_mfu_metrics=False, enable_mm_processor_stats=False, enable_logging_iteration_details=False), seed=0, served_model_name=Qwen/Qwen3-8B, enable_prefix_caching=True, enable_chunked_prefill=True, pooler_config=None, compilation_config={'mode': <CompilationMode.VLLM_COMPILE: 3>, 'debug_dump_path': None, 'cache_dir': '', 'compile_cache_save_format': 'binary', 'backend': 'inductor', 'custom_ops': ['none'], 'splitting_ops': ['vllm::unified_attention', 'vllm::unified_attention_with_output', 'vllm::unified_mla_attention', 'vllm::unified_mla_attention_with_output', 'vllm::mamba_mixer2', 'vllm::mamba_mixer', 'vllm::short_conv', 'vllm::linear_attention', 'vllm::plamo2_mamba_mixer', 'vllm::gdn_attention_core', 'vllm::olmo_hybrid_gdn_full_forward', 'vllm::kda_attention', 'vllm::sparse_attn_indexer', 'vllm::rocm_aiter_sparse_attn_indexer', 'vllm::unified_kv_cache_update', 'vllm::unified_mla_kv_cache_update'], 'compile_mm_encoder': False, 'cudagraph_mm_encoder': False, 'encoder_cudagraph_token_budgets': [], 'encoder_cudagraph_max_images_per_batch': 0, 'compile_sizes': [], 'compile_ranges_endpoints': [2048], 'inductor_compile_config': {'enable_auto_functionalized_v2': False, 'size_asserts': False, 'alignment_asserts': False, 'scalar_asserts': False, 'combo_kernels': True, 'benchmark_combo_kernel': True}, 'inductor_passes': {}, 'cudagraph_mode': <CUDAGraphMode.FULL_AND_PIECEWISE: (2, 1)>, 'cudagraph_num_of_warmups': 1, 'cudagraph_capture_sizes': [1, 2, 4, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128, 136, 144, 152, 160, 168, 176, 184, 192, 200, 208, 216, 224, 232, 240, 248, 256, 272, 288, 304, 320, 336, 352, 368, 384, 400, 416, 432, 448, 464, 480, 496, 512], 'cudagraph_copy_inputs': False, 'cudagraph_specialize_lora': True, 'use_inductor_graph_partition': False, 'pass_config': {'fuse_norm_quant': False, 'fuse_act_quant': False, 'fuse_attn_quant': False, 'enable_sp': False, 'fuse_gemm_comms': False, 'fuse_allreduce_rms': False}, 'max_cudagraph_capture_size': 512, 'dynamic_shapes_config': {'type': <DynamicShapesType.BACKED: 'backed'>, 'evaluate_guards': False, 'assume_32_bit_indexing': False}, 'local_cache_dir': None, 'fast_moe_cold_start': True, 'static_all_moe_layers': []}
(EngineCore pid=3380462) INFO 06-25 17:21:40 [parallel_state.py:1400] world_size=1 rank=0 local_rank=0 distributed_init_method=tcp://10.97.176.105:51235 backend=nccl
(EngineCore pid=3380462) INFO 06-25 17:21:46 [parallel_state.py:1716] rank 0 in world size 1 is assigned as DP rank 0, PP rank 0, PCP rank 0, TP rank 0, EP rank N/A, EPLB rank N/A
(EngineCore pid=3380462) INFO 06-25 17:21:46 [gpu_model_runner.py:4735] Starting to load model Qwen/Qwen3-8B...
(EngineCore pid=3380462) INFO 06-25 17:21:47 [cuda.py:334] Using FLASH_ATTN attention backend out of potential backends: ['FLASH_ATTN', 'FLASHINFER', 'TRITON_ATTN', 'FLEX_ATTENTION'].
(EngineCore pid=3380462) INFO 06-25 17:21:47 [flash_attn.py:596] Using FlashAttention version 2
(EngineCore pid=3380462) <frozen importlib._bootstrap_external>:1301: FutureWarning: The cuda.cudart module is deprecated and will be removed in a future release, please switch to use the cuda.bindings.runtime module instead.
(EngineCore pid=3380462) <frozen importlib._bootstrap_external>:1301: FutureWarning: The cuda.nvrtc module is deprecated and will be removed in a future release, please switch to use the cuda.bindings.nvrtc module instead.
Loading safetensors checkpoint shards: 100% Completed | 5/5 [00:02<00:00,  2.17it/s]
(EngineCore pid=3380462) 
(EngineCore pid=3380462) INFO 06-25 17:21:51 [default_loader.py:384] Loading weights took 2.35 seconds
(EngineCore pid=3380462) INFO 06-25 17:21:52 [gpu_model_runner.py:4820] Model loading took 15.27 GiB memory and 4.543456 seconds
(EngineCore pid=3380462) INFO 06-25 17:21:55 [backends.py:1051] Using cache directory: /home/darius/.cache/vllm/torch_compile_cache/7a48b06768/rank_0_0/backbone for vLLM's torch.compile
(EngineCore pid=3380462) INFO 06-25 17:21:55 [backends.py:1111] Dynamo bytecode transform time: 2.94 s
(EngineCore pid=3380462) INFO 06-25 17:21:56 [backends.py:285] Directly load the compiled graph(s) for compile range (1, 2048) from the cache, took 1.122 s
(EngineCore pid=3380462) INFO 06-25 17:21:56 [decorators.py:305] Directly load AOT compilation from path /home/darius/.cache/vllm/torch_compile_cache/torch_aot_compile/2cd01a1244334c3ed688a9a378065a03f678ea66021bf9cf5f7c5851c7cf2a1a/rank_0_0/model
(EngineCore pid=3380462) INFO 06-25 17:21:56 [monitor.py:48] torch.compile took 4.38 s in total
(EngineCore pid=3380462) INFO 06-25 17:21:56 [monitor.py:76] Initial profiling/warmup run took 0.11 s
(EngineCore pid=3380462) INFO 06-25 17:21:57 [kv_cache_utils.py:829] Overriding num_gpu_blocks=0 with num_gpu_blocks_override=512
(EngineCore pid=3380462) INFO 06-25 17:21:57 [gpu_model_runner.py:5876] Profiling CUDA graph memory: PIECEWISE=51 (largest=512), FULL=35 (largest=256)
(EngineCore pid=3380462) INFO 06-25 17:21:58 [gpu_model_runner.py:5955] Estimated CUDA graph memory: 2.35 GiB total
(EngineCore pid=3380462) INFO 06-25 17:21:58 [gpu_worker.py:436] Available KV cache memory: 19.36 GiB
(EngineCore pid=3380462) INFO 06-25 17:21:58 [gpu_worker.py:470] In v0.19, CUDA graph memory profiling will be enabled by default (VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=1), which more accurately accounts for CUDA graph memory during KV cache allocation. To try it now, set VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=1 and increase --gpu-memory-utilization from 0.9000 to 0.9596 to maintain the same effective KV cache size.
(EngineCore pid=3380462) INFO 06-25 17:21:58 [kv_cache_utils.py:1319] GPU KV cache size: 140,960 tokens
(EngineCore pid=3380462) INFO 06-25 17:21:58 [kv_cache_utils.py:1324] Maximum concurrency for 40,960 tokens per request: 3.44x
Capturing CUDA graphs (mixed prefill-decode, PIECEWISE): 100%|████████████████████████████████████████████████████████████████████████████████████████████████| 51/51 [00:02<00:00, 20.35it/s]
Capturing CUDA graphs (decode, FULL): 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 35/35 [00:01<00:00, 26.74it/s]
(EngineCore pid=3380462) INFO 06-25 17:22:03 [gpu_model_runner.py:6046] Graph capturing finished in 4 secs, took 2.44 GiB
(EngineCore pid=3380462) INFO 06-25 17:22:03 [gpu_worker.py:597] CUDA graph pool memory: 2.44 GiB (actual), 2.35 GiB (estimated), difference: 0.09 GiB (3.6%).
(EngineCore pid=3380462) INFO 06-25 17:22:03 [core.py:283] init engine (profile, create kv cache, warmup model) took 11.08 seconds
(EngineCore pid=3380462) INFO 06-25 17:22:06 [vllm.py:790] Asynchronous scheduling is enabled.
(APIServer pid=3380144) INFO 06-25 17:22:06 [api_server.py:592] Supported tasks: ['generate']
(APIServer pid=3380144) WARNING 06-25 17:22:06 [model.py:1435] Default vLLM sampling parameters have been overridden by the model's `generation_config.json`: `{'temperature': 0.6, 'top_k': 20, 'top_p': 0.95}`. If this is not intended, please relaunch vLLM instance with `--generation-config vllm`.
(APIServer pid=3380144) INFO 06-25 17:22:11 [hf.py:314] Detected the chat template content format to be 'string'. You can set `--chat-template-content-format` to override this.
(APIServer pid=3380144) INFO 06-25 17:22:11 [api_server.py:596] Starting vLLM server on http://172.17.0.1:8001
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:37] Available routes are:
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /openapi.json, Methods: HEAD, GET
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /docs, Methods: HEAD, GET
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /docs/oauth2-redirect, Methods: HEAD, GET
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /redoc, Methods: HEAD, GET
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /tokenize, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /detokenize, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /load, Methods: GET
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /version, Methods: GET
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /health, Methods: GET
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /metrics, Methods: GET
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /v1/models, Methods: GET
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /ping, Methods: GET
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /ping, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /invocations, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /v1/chat/completions, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /v1/chat/completions/batch, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /v1/responses, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /v1/responses/{response_id}, Methods: GET
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /v1/responses/{response_id}/cancel, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /v1/completions, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /v1/messages, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /v1/messages/count_tokens, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /inference/v1/generate, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /scale_elastic_ep, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /is_scaling_elastic_ep, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /v1/chat/completions/render, Methods: POST
(APIServer pid=3380144) INFO 06-25 17:22:11 [launcher.py:46] Route: /v1/completions/render, Methods: POST
(APIServer pid=3380144) INFO:     Started server process [3380144]
(APIServer pid=3380144) INFO:     Waiting for application startup.
(APIServer pid=3380144) INFO:     Application startup complete.
```

then can see GPU allocated

```bash
[25 Jun 05:26 PM] ~/Workspaces/tokenkaki ❯ nvidia-smi
Thu Jun 25 17:26:53 2026       
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
| N/A   37C    P0              58W / 275W |  39346MiB / 40960MiB |      0%      Default |
|                                         |                      |             Disabled |
+-----------------------------------------+----------------------+----------------------+
                                                                                         
+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
|    4   N/A  N/A   3380462      C   VLLM::EngineCore                          39336MiB |
+---------------------------------------------------------------------------------------+
```

lets dive abit deeper into the startup logs, because at this stage it is already interesting.

1. VRAM is preallocated at this point already

How is this done, where does the memory go towards?

  1. From `vllm/v1/worker/gpu_worker.py`, it takes a memory snapshot and computes allowed budget based on `cache_config.gpu_memory_utilization` which defaults to `0.9`. 
    This implies `~40 GiB * 0.9 = ~36 GiB requested budget`.
  2. Model weights are loaded. For Qwen3-8B at BF16, approx 16GB in model size from HF, and we can see in the logs `Model loading took 15.27 GiB memory and 4.359245 seconds` which is expected.
  3. Estimate the overhead for non-KV memory (e.g activations, other buffers and overhead) via profiling as per `vllm/v1/worker/gpu_worker.py` with `memory_profiling()`.
    This results in `available_kv_cache_memory = self.requested_memory - profile_result.non_kv_cache_memory`, which is logged as `Available KV cache memory: 19.36 GiB`.
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

      Given our available KV cache memory of 19.36 GiB, this means:
      - we have max number of blocks as `19.36 GiB total memory remaining / 2.25 MiB KV size per block = 8,810 blocks`, and then `8,810 blocks * 16 tokens/block = 140,960 token slots` which matches our logs, and
      - we can fit at most `19.36/5.625 = 3.44` concurrent full requests at the same time (i.e. maximum concurrency), which also matches our logs of 3.44x max concurrency (but we must also note that this max concurrency is theoretical, actual concurrency depends on prompts used and generation lengths).

Thus at the end our total usage = ~39GB, with breakdown as per:
```text
- A100 budget at 90%             ~36 GiB
  - model weights                  ~15.27 GiB
  - other profiled non-KV memory   (whatever remains before KV sizing)
- KV cache pool                  19.36 GiB
- CUDA graph capture             +2.44 GiB after KV allocation
```

2. Some optimizations are already enabled by default.

Flash Attention 2 is selected in this run:

```text
Using FLASH_ATTN attention backend out of potential backends: ['FLASH_ATTN', 'FLASHINFER', 'TRITON_ATTN', 'FLEX_ATTENTION'].
Using FlashAttention version 2
```

there are other backends too, todo: look into the diffs between backends

at this point we can test that the vllm endpoint is available, and we can run some initial tests to see if we can run inference

```bash
[25 Jun 05:31 PM] ~/Workspaces/tokenkaki ❯ VLLM_HOST=172.17.0.1 ./deploy/vllm/smoke-openai.sh
Checking vLLM models endpoint at http://172.17.0.1:8001/v1/models
{"object":"list","data":[{"id":"Qwen/Qwen3-8B","object":"model","created":1782379887,"owned_by":"vllm","root":"Qwen/Qwen3-8B","parent":null,"max_model_len":40960,"permission":[{"id":"modelperm-ba3edb09cf7a0d4d","object":"model_permission","created":1782379887,"allow_create_engine":false,"allow_sampling":true,"allow_logprobs":true,"allow_search_indices":false,"allow_view":true,"allow_fine_tuning":false,"organization":"*","group":null,"is_blocking":false}]}]}
Checking vLLM non-streaming chat completion for Qwen/Qwen3-8B
{"id":"chatcmpl-ad90799aa0b3359c","object":"chat.completion","created":1782379887,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"message":{"role":"assistant","content":"<think>\nOkay, the user wants me to reply with exactly \"tokenkaki-vllm-smoke-ok\". Let me check if there's any hidden request here. The phrase seems like a specific identifier or a test string. Maybe they're verifying if I can follow instructions precisely. I should make sure not to add any extra text. Just the exact string they provided. Alright, I'll respond with that.\n</think>\n\ntokenkaki-vllm-smoke-ok","refusal":null,"annotations":null,"audio":null,"function_call":null,"tool_calls":[],"reasoning":null},"logprobs":null,"finish_reason":"stop","stop_reason":null,"token_ids":null}],"service_tier":null,"system_fingerprint":null,"usage":{"prompt_tokens":21,"total_tokens":116,"completion_tokens":95,"prompt_tokens_details":null},"prompt_logprobs":null,"prompt_token_ids":null,"kv_transfer_params":null}
```

and now on the server side we can see
```bash
(APIServer pid=3380144) INFO:     10.97.176.105:56842 - "GET /v1/models HTTP/1.1" 200 OK
(APIServer pid=3380144) INFO:     10.97.176.105:56852 - "POST /v1/chat/completions HTTP/1.1" 200 OK
(APIServer pid=3380144) INFO 06-25 17:31:32 [loggers.py:259] Engine 000: Avg prompt throughput: 2.1 tokens/s, Avg generation throughput: 9.5 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 0.0%
(APIServer pid=3380144) INFO 06-25 17:31:42 [loggers.py:259] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 0.0 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 0.0%
```

congrats! model is served. we are done, and can now close shop lol. okay its not so simple.

lets try running it again identically, without restarting the server.

```bash
Checking vLLM models endpoint at http://172.17.0.1:8001/v1/models
{"object":"list","data":[{"id":"Qwen/Qwen3-8B","object":"model","created":1782379971,"owned_by":"vllm","root":"Qwen/Qwen3-8B","parent":null,"max_model_len":40960,"permission":[{"id":"modelperm-a6f02880c97fee78","object":"model_permission","created":1782379971,"allow_create_engine":false,"allow_sampling":true,"allow_logprobs":true,"allow_search_indices":false,"allow_view":true,"allow_fine_tuning":false,"organization":"*","group":null,"is_blocking":false}]}]}
Checking vLLM non-streaming chat completion for Qwen/Qwen3-8B
{"id":"chatcmpl-a47d509d7a3ac6fe","object":"chat.completion","created":1782379971,"model":"Qwen/Qwen3-8B","choices":[{"index":0,"message":{"role":"assistant","content":"<think>\nOkay, the user wants me to reply with exactly \"tokenkaki-vllm-smoke-ok\". Let me check if there's any hidden request here. The phrase seems like a specific identifier or a test string. Maybe they're verifying if I can follow instructions precisely. I should make sure not to add any extra text. Just the exact string they provided. Alright, I'll respond with that.\n</think>\n\ntokenkaki-vllm-smoke-ok","refusal":null,"annotations":null,"audio":null,"function_call":null,"tool_calls":[],"reasoning":null},"logprobs":null,"finish_reason":"stop","stop_reason":null,"token_ids":null}],"service_tier":null,"system_fingerprint":null,"usage":{"prompt_tokens":21,"total_tokens":116,"completion_tokens":95,"prompt_tokens_details":null},"prompt_logprobs":null,"prompt_token_ids":null,"kv_transfer_params":null}
```

```bash
(APIServer pid=3380144) INFO:     10.97.176.105:41936 - "GET /v1/models HTTP/1.1" 200 OK
(APIServer pid=3380144) INFO 06-25 17:32:52 [loggers.py:259] Engine 000: Avg prompt throughput: 0.5 tokens/s, Avg generation throughput: 5.2 tokens/s, Running: 1 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.1%, Prefix cache hit rate: 38.1%
(APIServer pid=3380144) INFO:     10.97.176.105:41952 - "POST /v1/chat/completions HTTP/1.1" 200 OK
(APIServer pid=3380144) INFO 06-25 17:33:02 [loggers.py:259] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 4.3 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 38.1%
(APIServer pid=3380144) INFO 06-25 17:33:12 [loggers.py:259] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 0.0 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 38.1%
```

something interesting to note in this quick run is that we can already see optimizations happening under the hood in vLLM from these logs. spot it?

its `Prefix cache hit rate: 38.1%`! we are using prefix caching already by default in vLLM. 
What does this mean?

TODO: explain [prefix caching](https://bentoml.com/llm/inference-optimization/prefix-caching)

So by theory since the request is identical, shouldnt the full prompt be cached?

In practice how is this number calculated in vLLM?

[Prefix Caching](https://docs.vllm.ai/en/v0.19.1/design/v1/prefix_caching.html)

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
(APIServer pid=3380144) INFO:     10.97.176.105:41314 - "GET /v1/models HTTP/1.1" 200 OK
(APIServer pid=3380144) INFO:     10.97.176.105:41330 - "POST /v1/chat/completions HTTP/1.1" 200 OK
(APIServer pid=3380144) INFO 06-25 17:34:22 [loggers.py:259] Engine 000: Avg prompt throughput: 0.5 tokens/s, Avg generation throughput: 9.5 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 50.8%
(APIServer pid=3380144) INFO 06-25 17:34:32 [loggers.py:259] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 0.0 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 50.8%
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

next, why is `GPU KV cache usage: 0.0%` for our examples above?

In vLLM 0.19.1, the log value comes from:

- `scheduler.py`: `kv_cache_usage=self.kv_cache_manager.usage`
- `kv_cache_manager.py`: returns `self.block_pool.get_usage()`
- `block_pool.py`: `1.0 - free_blocks / total_gpu_blocks`
So this metric is basically current KV block occupancy.

```text
prompt_tokens = 21
total_tokens = 116
block_size = 16
ceil(116 / 16) = 8 blocks
8 / 8810 blocks = ~0.09%
```

So while the request is sampled as active, it rounds to about 0.1%. If the log samples after completion, it shows 0.0%.

So if we increase the length of prompt, we should see an increase in this value right? Assuming that the log samples while the request is still active.

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
(APIServer pid=3380144) INFO 06-25 17:35:32 [loggers.py:259] Engine 000: Avg prompt throughput: 3602.5 tokens/s, Avg generation throughput: 7.6 tokens/s, Running: 1 reqs, Waiting: 0 reqs, GPU KV cache usage: 25.6%, Prefix cache hit rate: 0.1%
(APIServer pid=3380144) INFO 06-25 17:35:42 [loggers.py:259] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 58.8 tokens/s, Running: 1 reqs, Waiting: 0 reqs, GPU KV cache usage: 26.0%, Prefix cache hit rate: 0.1%
(APIServer pid=3380144) INFO 06-25 17:35:52 [loggers.py:259] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 58.6 tokens/s, Running: 1 reqs, Waiting: 0 reqs, GPU KV cache usage: 26.5%, Prefix cache hit rate: 0.1%
(APIServer pid=3380144) INFO:     10.97.176.105:52268 - "POST /v1/chat/completions HTTP/1.1" 200 OK
(APIServer pid=3380144) INFO 06-25 17:36:02 [loggers.py:259] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 15.5 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 0.1%
(APIServer pid=3380144) INFO 06-25 17:36:12 [loggers.py:259] Engine 000: Avg prompt throughput: 0.0 tokens/s, Avg generation throughput: 0.0 tokens/s, Running: 0 reqs, Waiting: 0 reqs, GPU KV cache usage: 0.0%, Prefix cache hit rate: 0.1%
```

response from the server:
```json
{
  "prompt_tokens": 36025,
  "total_tokens": 37430,
  "completion_tokens": 1405,
  "prompt_tokens_details": null
}
```

therefore this is coherent, because given block_size 16 and the prefill phase taking the full input prompt length:
```text
ceil(36,025 / 16) = 2,252 blocks
2,252 / 8,810 = 25.56%
```
where 8810 is from the startup logs where we previously calculated to be the maximum number of blocks allowed on our hardware due to VRAM size.

then, as the generation continues into the decode phase and completes decode:
```text
ceil(37,544 / 16) = 2,347 blocks
2,347 / 8,810 = 26.64%
```
which is near 26.5% from the logs. likely not exact match because of logging sampling frequency.

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
UV_TORCH_BACKEND=auto \
uv run vllm bench latency \
  --model Qwen/Qwen3-8B \
  --batch-size 1 \
  --input-len 128 \
  --output-len 64 \
  --num-iters-warmup 10 \
  --num-iters 30 \
  --output-json ../../experiments/2_vllm_0.19_Qwen3-8B/1_latency/vllm-latency-qwen3-8b-a100.json
```


benchmark 2: throughput

```bash
cd /home/darius/Workspaces/tokenkaki/deploy/vllm

CUDA_DEVICE_ORDER=PCI_BUS_ID \
CUDA_VISIBLE_DEVICES=4 \
UV_TORCH_BACKEND=auto \
uv run vllm bench throughput \
  --backend vllm \
  --model Qwen/Qwen3-8B \
  --dataset-name random \
  --num-prompts 100 \
  --random-input-len 128 \
  --random-output-len 64 \
  --random-range-ratio 0.0 \
  --output-json ../../experiments/2_vllm_0.19_Qwen3-8B/2_throughput/vllm-throughput-qwen3-8b-a100.json
```

benchmark 3: direct OpenAI-compatible serving

```bash
BENCHMARK_TARGET=vllm \
VLLM_BASE_URL=http://172.17.0.1:8001 \
EXPERIMENT_ROOT=experiments/2_vllm_0.19_Qwen3-8B \
NUM_PROMPTS=100 \
REQUEST_RATE=5 \
RANDOM_INPUT_LEN=128 \
RANDOM_OUTPUT_LEN=64 \
RESULT_FILENAME=vllm-direct-serving-qwen3-8b-a100.json \
./benchmarks/vllm-serving-bench.sh
```

results from the saved artifacts:

```text
latency, batch=1, 128 input / 64 output:
- avg: 0.8452 s
- p50: 0.8451 s
- p99: 0.8469 s

offline throughput, 100 prompts:
- 45.08 requests/s
- 8,654.63 total tokens/s

direct serving, 100 prompts at 5 RPS:
- 100 successful, 0 failed
- 4.79 req/s observed throughput
- 306.38 output tok/s
- 919.14 total tok/s
- peak output throughput 651.00 output tok/s
- peak concurrent requests 17
- mean TTFT 48.19 ms, p99 TTFT 60.09 ms
- mean TPOT 13.72 ms, p99 TPOT 14.46 ms
- mean ITL 13.51 ms, p99 ITL 20.35 ms
```

The direct serving result above comes from:

```text
experiments/2_vllm_0.19_Qwen3-8B/3_direct_vllm_serve/out.log
experiments/2_vllm_0.19_Qwen3-8B/3_direct_vllm_serve/vllm-direct-serving-qwen3-8b-a100.json
```

I also ran a `--save-detailed` diagnostic immediately after the summary run:

```text
experiments/2_vllm_0.19_Qwen3-8B/3_direct_vllm_serve/out-detailed.log
experiments/2_vllm_0.19_Qwen3-8B/3_direct_vllm_serve/vllm-direct-serving-qwen3-8b-a100-detailed.json
```

these 3 benchmarks becomes the baseline for future experiments, because they are the raw measurements for a static workload on this hardware directly at the vLLM level.

later when we add additional platform infrastructure like gateway, queues, etc, or further optimizations in the vLLM <> hardware level, we will fall back onto these baseline experiments for comparison.

for latency:
- it is the smallest engine-only check: batch size 1, 128 input tokens, 64 output tokens. 
- It averaged 0.845s, with p99 at 0.847s.
- there is barely any spread here, so for this exact synthetic request shape, this vLLM engine run is very stable on one A100. 
- But this is not production serving latency.

for throughput:
- again another engine-only check
- 100 synthetic prompts at 45.08 req/s and 8,654.63 total tokens/s.
- But this is not production serving throughput too.

for direct vllm serving:
- it is the first OpenAI-compatible endpoint baseline. 
- At a target 5 RPS, all 100 requests completed with 0 failures. Observed throughput was 4.79 req/s. Mean TTFT was about 50ms, p99 TTFT was about 80ms, mean TPOT was about 13.7ms, and p99 TPOT was about 14.5ms. 
- This is the benchmark that I care most about at this point before adding the gateway, because it measures the public HTTP path into vLLM by itself.
- This matters for tokenkaki because the gateway should start out boring and mostly transparent. When I run the same serving benchmark through `benchmark -> gateway -> vLLM`, this run above becomes the comparison point. If TTFT, TPOT, failure rate, throughput, or concurrency look much worse, then I have somewhere concrete to look: routing, streaming, HTTP forwarding, serialization, connection reuse, or container networking.

The limitation is also important. This is synthetic, fixed at 128 input / 64 output tokens, using one selected A100, one model, one vLLM version, and only 100 prompts. There is no mixed prompt distribution, no long-context pressure, no sustained soak test, no gateway yet, and no Prometheus/DCGM correlation with GPU/system metrics. So these are starting points with provenance, not general claims about Qwen3-8B serving performance.

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

from the results, we can see

```text
============ Serving Benchmark Result ============
Successful requests:                     100       
Failed requests:                         0         
Request rate configured (RPS):           5.00      
Benchmark duration (s):                  20.94     
Total input tokens:                      12800     
Total generated tokens:                  6400      
Request throughput (req/s):              4.77      
Output token throughput (tok/s):         305.58    
Peak output token throughput (tok/s):    653.00    
Peak concurrent requests:                17.00     
Total token throughput (tok/s):          916.75    
---------------Time to First Token----------------
Mean TTFT (ms):                          87.86     
Median TTFT (ms):                        79.05     
P99 TTFT (ms):                           172.18    
-----Time per Output Token (excl. 1st token)------
Mean TPOT (ms):                          13.72     
Median TPOT (ms):                        13.67     
P99 TPOT (ms):                           14.63     
---------------Inter-token Latency----------------
Mean ITL (ms):                           13.50     
Median ITL (ms):                         13.20     
P99 ITL (ms):                            37.17     
==================================================
```

the interesting thing comes when we compare against benchmark 3. there is a difference in TTFT!

```text
---------------Time to First Token----------------
Mean TTFT (ms):                          50.08     
Median TTFT (ms):                        48.10     
P99 TTFT (ms):                           80.02     
```

the other metrics remain largely the same except for TTFT.

Our TTFT extended by average of 37.78ms just by adding the gateway. That feels quite long because its a 75% increase in TTFT on average, and on worst case P99, it increased by 92.16ms - more than 2x increase.

Why? Where in the gateway is causing this increase in latency?

Our current gateway still lacks detailed trace metrics to be able to find out the reason, so we will need to add that.

Added new prometheus metrics to track the different stages of the gateway.

backend_open = gateway request received -> vLLM headers
first_backend_chunk = vLLM headers -> first vLLM chunk
first_chunk_relay = first vLLM chunk -> gateway yield to client

and finally, first_client_chunk = gateway request received -> gateway yield to client
where 
first_client_chunk ~= request parsing/routing
                    + backend_open
                    + first_backend_chunk
                    + first_chunk_relay

rerunning the benchmark, we again see an increased TTFT.

```text
---------------Time to First Token----------------
Mean TTFT (ms):                          87.75     
Median TTFT (ms):                        78.34     
P99 TTFT (ms):                           165.79    
```

then from the prom metrics, we can get summaries generated by `benchmarks/gateway-timing-summary.py`:
```json
"gateway_stream_timing_ms": {
  "backend_open": {
    "count": 100.0,
    "sum_ms": 3890.5343897640705,
    "mean_ms": 38.905343897640705,
    "bucket_counts_s": {
      "0.005": 0.0,
      "0.01": 0.0,
      "0.025": 0.0,
      "0.05": 81.0,
      "0.075": 97.0,
      "0.1": 98.0,
      "0.25": 100.0
    }
  },
  "first_backend_chunk": {
    "count": 100.0,
    "sum_ms": 4426.112852990627,
    "mean_ms": 44.26112852990627,
    "bucket_counts_s": {
      "0.005": 1.0,
      "0.01": 1.0,
      "0.025": 3.0,
      "0.05": 77.0,
      "0.075": 98.0,
      "0.1": 100.0
    }
  },
  "first_client_chunk": {
    "count": 100.0,
    "sum_ms": 8413.913410156965,
    "mean_ms": 84.13913410156965,
    "bucket_counts_s": {
      "0.005": 0.0,
      "0.01": 0.0,
      "0.025": 0.0,
      "0.05": 0.0,
      "0.075": 42.0,
      "0.1": 80.0,
      "0.25": 100.0
    }
  },
  "first_chunk_relay": {
    "count": 100.0,
    "sum_ms": 0.015605241060256958,
    "mean_ms": 0.00015605241060256958,
    "bucket_counts_s": {
      "0.005": 100.0
    }
  }
}
```

from this result, we can see that:

- `backend_open` 
  - mean is `38.9ms`.
    - this is the time from "gateway starts opening the backend stream" to "gateway receives backend response headers".
    - this includes the creation of a fresh `httpx.AsyncClient` every request, the extra HTTP hop from the gateway container to `host.docker.internal:8001`, the `httpx` stream setup, and whatever vLLM needs to accept the request and return headers.
    - this number is very close to the average TTFT delta between direct vLLM and gateway serving:
      - direct vLLM mean TTFT: `50.08ms`
      - gateway mean TTFT: `87.75ms`
      - delta: `37.67ms`
    - so the average overhead is not mysterious anymore. it is basically the added backend stream-open path.
  - the backend-open tail is visible, but not exact.
    - `81` requests were `<= 50ms`
    - `97` requests were `<= 75ms`
    - `98` requests were `<= 100ms`
    - `100` requests were `<= 250ms`
    - with only these histogram buckets, the actual P99 backend-open value is somewhere between `100ms` and `250ms`.
    - this is too coarse to identify the exact slow request, but it is enough to show that the gateway path has tail latency before the first token even starts flowing back.

- `first_backend_chunk` 
  - mean is `44.26ms`.
  - this is the time after backend headers, until the first SSE chunk arrives back at the gateway.
  - this part is mostly vLLM-side work after request admission: scheduling, prefill/first-token work, and getting the first chunk into the stream.
  - this is not "gateway overhead" in the same way as `backend_open`; it is still on the serving path, but it belongs to the backend response phase.

- `first_chunk_relay` 
  - mean is effectively `0ms`.
  - once the gateway receives the first backend chunk, yielding it back to the client is not where the extra TTFT is going.
  - so the first conclusion is not "Python streaming is slow".
  - the better conclusion is: the extra TTFT comes before the first chunk reaches the gateway, especially from opening the backend stream.

- `first_client_chunk` 
  - mean is `84.14ms`.
  - this is the gateway-observed first-token time from request receipt to the first chunk being yielded back to the benchmark client.
  - it lines up with the benchmark-observed mean TTFT of `87.75ms`, which is good. it means our gateway-side metrics are measuring the same shape as the external benchmark, with a few ms of client/network measurement difference.

Therefore, from this we can conclude that:

- Direct vLLM serving gives us the baseline OpenAI-compatible HTTP path.
- Adding the gateway keeps throughput and TPOT basically the same for this workload.
- Adding the gateway increases TTFT by around `38ms` on average.
- The new gateway timing metrics show that this average increase is almost exactly the `backend_open` stage.

next question is: given that we have this overhead added in backend_open, what can we do to reduce this?
likely cause of the overhead should be the multiple creations of a new http client per request.
what we can do to resolve this is to add a gateway-owned shared httpx.AsyncClient on app startup/lifespan.

Added new logic for shared `httpx.AsyncClient` per gateway process, instead of creating a fresh client on every forwarded request.

rerunning the same benchmark again under `6_gateway_serve_pooled-client`, we get:

```text
---------------Time to First Token----------------
Mean TTFT (ms):                          51.85
Median TTFT (ms):                        50.13
P99 TTFT (ms):                           84.31
```

and from the gateway timing summary:

```json
"gateway_stream_timing_ms": {
  "backend_open": {
    "count": 100.0,
    "mean_ms": 7.331884279847145
  },
  "first_backend_chunk": {
    "count": 100.0,
    "mean_ms": 42.31208797544241
  },
  "first_client_chunk": {
    "count": 100.0,
    "mean_ms": 49.89084303379059
  },
  "first_chunk_relay": {
    "count": 100.0,
    "mean_ms": 0.0002800673246383667
  }
}
```

from this result, we can see that:

- `backend_open`
  - improved from `38.9ms` to `7.33ms`.
  - this is a reduction of around `31.6ms`.
  - this is the stage that changed the most after adding a shared backend client.
- `first_backend_chunk`
  - stayed roughly the same:
    - before: `44.26ms`
    - after: `42.31ms`
  - this means the vLLM-side first-token phase did not materially change.
- `first_chunk_relay`
  - remained effectively `0ms`.
  - so again, the Python async streaming relay is not where the cost is.
- `first_client_chunk`
  - improved from `84.14ms` to `49.89ms`.
  - this lines up with the benchmark-observed TTFT improvement:
    - before pooled client: `87.75ms`
    - after pooled client: `51.85ms`

Therefore, from this experiment we can conclude that:

- The extra gateway TTFT was mostly self-inflicted by per-request backend HTTP client/connection setup.
- Reusing a gateway-owned `httpx.AsyncClient` removes most of that overhead.
- The gateway path now has TTFT much closer to direct vLLM serving:
  - direct vLLM mean TTFT: `50.08ms`
  - gateway with pooled client mean TTFT: `51.85ms`
  - remaining mean delta: `1.77ms`
- TPOT and throughput remain basically unchanged, which is what we want. We improved the request-open path without changing the model serving phase.

does this make sense for actual prod serving?

yes, this is closer to what a real production gateway should do.

Creating a new HTTP client per request is usually not the right production shape. The client owns connection pools, keepalive behavior, socket reuse, and pool-level limits. If we recreate it every request, we throw away the main thing that makes the backend HTTP hop cheap.

But the production version should be a little more explicit than the current experiment code:
- create one shared async client per gateway process, or one per backend/upstream pool.
- create it during app startup/lifespan, and close it during shutdown.
- configure explicit connection limits:
  - max total connections
  - max keepalive connections
  - keepalive expiry
- configure explicit timeouts:
  - connect timeout
  - read timeout
  - write timeout
  - pool timeout
- expose metrics for backend open time, backend read time, pool pressure, errors, and timeout classes.
- if the gateway has multiple backend replicas later, use separate pools per backend target or per routing group instead of one anonymous global client.

The conclusion is:
- naive gateway: creates a new backend client every request, adds ~`38ms` mean TTFT.
- pooled gateway: reuses backend HTTP connections, adds only ~`1-2ms` mean TTFT over direct vLLM for this benchmark.
- for production, a pooled async backend client is the correct direction, but it should become an explicit, configured gateway resource rather than an accidental global.

---

TODO: how this leads to milestone 2 / next post
