# 언어모델의 계산을 해부하다

이 저장소는 현대 decoder-only Transformer가 입력 토큰에서 다음 토큰을 생성하기까지의 계산을 수식, 텐서 shape, 구현 관점과 기계론적 해석가능성 관점에서 설명하는 한국어 학습서다. 목표는 순전파를 정확히 계산할 수 있는 수준을 넘어, 학습된 모델이 내부에서 어떤 표현·회로·알고리즘을 구현하는지 연구할 수 있는 기반을 만드는 것이다.

완성된 PDF는 A4 90쪽이며, [`output/pdf/llm-mechanisms-book.pdf`](output/pdf/llm-mechanisms-book.pdf)에서 읽을 수 있다.

## 학습 경로

| 단계 | 주제 | 도달 목표 |
|---:|---|---|
| 1 | 신경망 표현의 수학 | 벡터, 활성값, 표현과 확률 분포를 계산한다. |
| 2 | Transformer 순전파 | 토큰화부터 logits와 다음 토큰 선택까지를 추적한다. |
| 3 | 현대 decoder-only LLM | RMSNorm, RoPE, SwiGLU, GQA, KV cache를 구분한다. |
| 4 | 표현 분석 | feature direction, superposition, logit lens의 의미와 한계를 안다. |
| 5 | 회로 | residual stream, attention head, MLP feature와 induction head를 연결한다. |
| 6 | 인과적 해석 | ablation, activation patching, causal tracing의 추론 범위를 평가한다. |
| 7 | 행동 메커니즘 | 사실 회상, 복사, 추론, 거절과 환각을 연구 문헌으로 분석한다. |

각 단계는 앞 단계의 전제를 명시한다. 특히 Transformer 수식을 안다는 사실과 특정 행동을 만드는 내부 알고리즘을 안다는 사실은 서로 다르므로, 순전파의 정의와 기계론적 해석을 분리해 다룬다.

## 시작하기

처음 읽는다면 Phase 1부터 Phase 3까지를 순서대로 읽은 뒤, 관심 있는 행동에 따라 Phase 4부터 Phase 7로 넘어간다. `Decoder-only Transformer의 정확한 순전파` 장은 입력 텐서·QKV·causal attention·MLP·residual stream·LM head가 어떻게 연결되는지 수식과 shape로 설명한다.

원고를 수정하거나 직접 빌드하려면 아래 명령을 실행한다.

```bash
make pdf
```

빌드에는 LuaLaTeX, BibTeX, `luatexko`, TeX Gyre 글꼴과 UnFonts가 필요하다. 생성된 PDF는 `main.pdf`다.

## 디렉터리 구조

```text
.
├── frontmatter/    # 목적, 증거 기준, 학습 지도
├── chapters/       # Phase 1–7과 결론
├── appendices/     # 표기법, 유도, 재현 실험, 주장 감사표
├── output/pdf/     # 읽기용 완성 PDF
├── main.tex        # 책의 진입점
├── preamble.tex    # 공통 수식·조판 설정
└── references.bib  # 참고문헌
```

## 증거 기준

수학적 등식과 공개 구현의 동작은 직접 검산한다. 경험적 주장은 모델, 데이터, 개입, 평가 범위를 함께 적고 원 논문을 인용한다.

관찰된 활성값 패턴, 인과적 개입으로 확인한 기여, 저자의 해석은 서로 다른 종류의 주장이다. 한 모델·과제·프롬프트에서 얻은 결과를 모든 언어모델의 일반적 메커니즘으로 확대하지 않는다.

## 한계와 사용 범위

주어진 가중치와 입력에 대해 순전파 텐서가 어떻게 계산되는지는 완전히 정의할 수 있다. 그러나 대규모 언어모델이 학습한 모든 의미적 feature와 알고리즘을 완전하게 해석하는 방법은 아직 확립되지 않았다.

따라서 이 책은 확정된 수학적 사실과 해당 문헌이 제시한 경험적 증거를 구분한다. 이 책은 특정 상용 모델의 내부를 완전하게 설명한다고 주장하지 않는다.
