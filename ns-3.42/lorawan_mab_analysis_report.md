# Rapport d'Analyse LoRaWAN MAB

Date: 2025-07-23 23:31:38

## Résumé Exécutif

- **Expériences analysées**: 27
- **Scénarios**: JOINT_CH_SF, SF_ONLY
- **Modes MAB**: MAB_COMBINATORIAL, MAB_RANDOM, MAB_INDEPENDENT
- **Tailles de réseau**: [3, 9, 15, 30]

## Performances Moyennes

| Mode MAB | FSR Moyen | Fairness Moyen | Diversité SF |
|----------|-----------|----------------|-------------|
| MAB_COMBINATORIAL | 0.0278 | 0.1120 | 1.46 |
| MAB_RANDOM | 0.0243 | 0.1296 | 1.75 |
| MAB_INDEPENDENT | 0.0185 | 0.1111 | 1.17 |

## Meilleures Configurations

- **Meilleure FSR**: 0.0833 (MAB_COMBINATORIAL - SF_ONLY - 3 devices)
- **Meilleure Fairness**: 0.1667 (MAB_COMBINATORIAL - SF_ONLY - 3 devices)
- **Meilleure Diversité SF**: 3 (MAB_COMBINATORIAL - SF_ONLY - 9 devices)
