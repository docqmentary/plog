# Engineering Appendix

## A. Rank Prediction (Lightweight)
- Feature: x = log1p(V)  # Naver last-month total searches
- Target: R in [1..1001]; 1001 == 'not found in Top1000' (right-censoring surrogate)
- Model options:
  1) Quantile-bin median mapping (robust & simple)
  2) Monotonic spline regression (downweight R=1001)
- Prediction: R_hat = round(f(x*)); if R_hat > 1000 → display '1000+'

## B. Handling 1000+
- Store R=1001.
- Training: treat as right-censored or assign low weight.
- Display: '1000+' only (never show 1001).

## C. Naver Top1000 Probe (Pseudo)
Loop display=100, start=1..1000, sort='sim'; stop when my URL matches. Else return 1001.

## D. External References Evaluation (Search OFF)
- Provide the 10 collected URLs to the model with external_search=false.
- Score: low advertisement signals, authenticity, engagement, recency, H2/H3 structure, keyword match.
- Return TopN cards.
