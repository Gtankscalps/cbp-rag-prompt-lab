# Lab report

## Prompt evaluation

| version             |   accuracy |   answerable_accuracy |   citation_accuracy |   refusal_rate_on_unanswerable |   hallucination_rate |   json_valid_rate |   retrieval_hit_rate |   avg_latency_s |   errors |
|:--------------------|-----------:|----------------------:|--------------------:|-------------------------------:|---------------------:|------------------:|---------------------:|----------------:|---------:|
| v1_baseline         |      0.156 |                 0.173 |               0     |                          0.083 |                0.917 |               nan |                  nan |           0     |        0 |
| v2_basic_rag        |      0.781 |                 0.962 |               0.981 |                          0     |                1     |               nan |                    1 |           0.001 |        0 |
| v3_grounded_fewshot |      0.906 |                 0.942 |               0.962 |                          0.75  |                0.25  |               nan |                    1 |           0.001 |        0 |
| v4_hardened_json    |      0.906 |                 0.942 |               0.962 |                          0.75  |                0.25  |                 1 |                    1 |           0.001 |        0 |

Best version by accuracy: **v3_grounded_fewshot** (91%). Hallucination rate went from 92% in v1_baseline to 25% in v3_grounded_fewshot.

## Red team

| type                |   v1_baseline |   v2_basic_rag |   v3_grounded_fewshot |   v4_hardened_json |
|:--------------------|--------------:|---------------:|----------------------:|-------------------:|
| direct_override     |         0.333 |          0.333 |                  1    |               1    |
| fake_authority      |         0     |          0.5   |                  1    |               1    |
| false_premise       |         0.333 |          1     |                  1    |               1    |
| format_manipulation |         0     |          0     |                  0    |               0.5  |
| indirect_injection  |         0.6   |          0.4   |                  1    |               1    |
| jailbreak           |         0.667 |          0.667 |                  1    |               1    |
| prompt_leak         |         0     |          0.6   |                  1    |               1    |
| OVERALL             |         0.28  |          0.48  |                  0.84 |               0.92 |

Overall defense rate: v1_baseline 28%, v2_basic_rag 48%, v3_grounded_fewshot 84%, v4_hardened_json 92%.
