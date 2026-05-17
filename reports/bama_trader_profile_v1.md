# BAMA Trader Profile v1

Source: `data/NT8_all_trades_2021_2026_APEX.csv`

## 1. Resume global

- PnL total: -2106.00 $
- Nombre total de trades: 90
- Win rate: 57.78%
- Trade moyen: -23.40 $
- Plus gros gain: 500.00 $
- Plus grosse perte: -825.00 $
- MAE moyen: 145.76 $
- MFE moyen: 107.68 $

## 2. Analyse temporelle

### Meilleures heures
- 18:00: PnL 878.50 $, trades 12, win rate 75.00%, moyenne 73.21 $
- 16:00: PnL 530.50 $, trades 5, win rate 100.00%, moyenne 106.10 $
- 21:00: PnL 333.00 $, trades 4, win rate 50.00%, moyenne 83.25 $
- 17:00: PnL 294.50 $, trades 18, win rate 66.67%, moyenne 16.36 $
- 14:00: PnL -5.00 $, trades 3, win rate 0.00%, moyenne -1.67 $

### Pires heures
- 20:00: PnL -2917.50 $, trades 28, win rate 50.00%, moyenne -104.20 $
- 19:00: PnL -925.00 $, trades 18, win rate 55.56%, moyenne -51.39 $
- 09:00: PnL -295.00 $, trades 2, win rate 0.00%, moyenne -147.50 $
- 14:00: PnL -5.00 $, trades 3, win rate 0.00%, moyenne -1.67 $
- 17:00: PnL 294.50 $, trades 18, win rate 66.67%, moyenne 16.36 $

### Meilleures journees
- 2026-01-08: PnL 1030.50 $, trades 10, win rate 70.00%, moyenne 103.05 $
- 2025-12-19: PnL 1000.00 $, trades 3, win rate 100.00%, moyenne 333.33 $
- 2026-01-21: PnL 585.00 $, trades 3, win rate 100.00%, moyenne 195.00 $
- 2026-01-20: PnL 430.00 $, trades 1, win rate 100.00%, moyenne 430.00 $
- 2026-01-07: PnL 425.00 $, trades 4, win rate 75.00%, moyenne 106.25 $

### Pires journees
- 2025-12-15: PnL -2515.00 $, trades 12, win rate 33.33%, moyenne -209.58 $
- 2026-01-09: PnL -2075.50 $, trades 11, win rate 36.36%, moyenne -188.68 $
- 2026-01-28: PnL -995.00 $, trades 3, win rate 33.33%, moyenne -331.67 $
- 2026-01-23: PnL -437.00 $, trades 2, win rate 0.00%, moyenne -218.50 $
- 2026-01-02: PnL -412.50 $, trades 1, win rate 0.00%, moyenne -412.50 $

### Heures du soir (18:00-23:59)
- Trades: 62
- PnL: -2631.00 $
- Win rate: 56.45%
- Trade moyen: -42.44 $
- Duree moyenne: 1.48 min

## 3. Analyse comportementale

- Serie maximale de pertes: 8 trades consecutifs
- Nombre de series de pertes de 3 trades ou plus: 4
- Jours en surtrading (>10 trades): 2
- Trades destructeurs identifies: 1 plus bas extreme, avec top 5 ci-dessous

### Top 5 trades destructeurs
- 2025-12-15 20:12:03: -825.00 $, qty 3, MAE 915.00 $, MFE 15.00 $
- 2026-01-09 19:00:36: -810.00 $, qty 3, MAE 810.00 $, MFE 30.00 $
- 2026-01-28 17:31:15: -645.00 $, qty 3, MAE 690.00 $, MFE 150.00 $
- 2025-12-15 20:12:03: -560.00 $, qty 2, MAE 610.00 $, MFE 10.00 $
- 2025-12-15 20:12:03: -540.00 $, qty 2, MAE 610.00 $, MFE 10.00 $

### Gagnants vs perdants
- Trades gagnants: 52, moyenne 117.63 $, duree moyenne 1.26 min, MAE 69.38 $, MFE 142.77 $
- Trades perdants: 38, moyenne -216.39 $, duree moyenne 1.92 min, MAE 250.28 $, MFE 59.67 $

## 4. Analyse Apex

- Limite journaliere proposee: stop a -900 $ realise.
- Nombre optimal de trades: 10 trades maximum par jour.
- Configurations de taille a surveiller: pertes concentrees sur les trades multi-contrats quand le MAE depasse le MFE.
- Horaires a eviter: 19:00, 20:00
- Protection recommandee: arret immediat apres 3 pertes consecutives ou apres une perte unitaire superieure a 50% de la limite journaliere.
- Protection recommandee: pause obligatoire apres un trade perdant dont le MAE est superieur au MFE.
- Protection recommandee: ne pas augmenter la taille pendant une sequence perdante.

### Lecture par nombre de trades
- 10 trades/jour: 2 jour(s), PnL total 958.00 $, moyenne/jour 479.00 $
- 4 trades/jour: 1 jour(s), PnL total 425.00 $, moyenne/jour 425.00 $
- 7 trades/jour: 1 jour(s), PnL total 143.00 $, moyenne/jour 143.00 $
- 3 trades/jour: 6 jour(s), PnL total 649.00 $, moyenne/jour 108.17 $
- 1 trades/jour: 3 jour(s), PnL total 297.50 $, moyenne/jour 99.17 $

## 5. Conclusion finale

- Profil trader: win rate eleve (57.78%) mais expectancy negatif avec un trade moyen de -23.40 $.
- Style detecte: scalping tres court terme, avec duree moyenne gagnants 1.26 min et perdants 1.92 min.
- Principaux risques: pertes unitaires lourdes, sequences de pertes jusqu'a 8, et degradation possible lors des sessions du soir (PnL soir -2631.00 $).
- Points forts: capacite a generer plus de trades gagnants que perdants et presence de gains unitaires significatifs.
- Priorite operationnelle: reduire la taille ou arreter la session avant le trade 11, puis verrouiller le stop journalier propose.
