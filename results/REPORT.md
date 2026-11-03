# Lab report

## Prompt evaluation

| version             |   accuracy |   answerable_accuracy |   citation_accuracy |   refusal_rate_on_unanswerable |   hallucination_rate |   json_valid_rate |   retrieval_hit_rate |   avg_latency_s |   errors |
|:--------------------|-----------:|----------------------:|--------------------:|-------------------------------:|---------------------:|------------------:|---------------------:|----------------:|---------:|
| v1_baseline         |      0.265 |                 0.286 |               0     |                          0.167 |                0.833 |               nan |                  nan |               0 |        0 |
| v2_basic_rag        |      0.794 |                 0.964 |               0.964 |                          0     |                1     |               nan |                    1 |               0 |        0 |
| v3_grounded_fewshot |      0.941 |                 0.929 |               0.929 |                          1     |                0     |               nan |                    1 |               0 |        0 |
| v4_hardened_json    |      0.941 |                 0.929 |               0.929 |                          1     |                0     |                 1 |                    1 |               0 |        0 |

Best version by accuracy: **v3_grounded_fewshot** (94%). Hallucination rate went from 83% in v1_baseline to 0% in v3_grounded_fewshot.

## Red team

| type                |   v1_baseline |   v2_basic_rag |   v3_grounded_fewshot |   v4_hardened_json |
|:--------------------|--------------:|---------------:|----------------------:|-------------------:|
| direct_override     |         0     |          0     |                 1     |                  1 |
| fake_authority      |         0     |          0     |                 1     |                  1 |
| false_premise       |         0     |          1     |                 1     |                  1 |
| format_manipulation |         0     |          0     |                 0     |                  1 |
| indirect_injection  |         0.667 |          0     |                 1     |                  1 |
| jailbreak           |         0     |          0     |                 1     |                  1 |
| prompt_leak         |         0     |          0.667 |                 1     |                  1 |
| OVERALL             |         0.154 |          0.231 |                 0.846 |                  1 |

Overall defense rate: v1_baseline 15%, v2_basic_rag 23%, v3_grounded_fewshot 85%, v4_hardened_json 100%.
