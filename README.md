# SecureRegister – TP Sécurité des Mots de Passe
## Hugo PIGEON - Anthony LAVOUTE

## Description du projet
Ce projet est un mini site web composé de :
- un **frontend (Flask)**,
- un **backend (Node.js + TypeScript)**,
- une **base de données (PostgreSQL)**.

L’objectif est de mettre en place un système d’inscription et d’authentification sécurisés, basé sur :
- la vérification de l’entropie et de la redondance des mots de passe,
- l’utilisation d’un **Bloom Filter** pour vérifier si un mot de passe a fuité (wordlist : *rockyou.txt*),
- des règles classiques de robustesse (longueur minimale, majuscules, minuscules, chiffres, etc.).

Le projet est entièrement conteneurisé avec Docker et Docker Compose.

---

## Architecture des services

### 1. Base de données (PostgreSQL)
- Conteneur : `postgres_db`
- Image : `postgres:16-alpine`
- Stocke les informations d’utilisateurs inscrits (login + mot de passe hashé).

### 2. Backend (Node.js + TypeScript)
- Conteneur : `backend_node_ts`
- Port exposé : `3000`
- Rôles :
  - Communication avec la base de données.
  - Vérification de la sécurité du mot de passe (entropie, redondance, règles classiques).
  - Vérification via **Bloom Filter** que le mot de passe n’appartient pas à *rockyou.txt*.
  - Fourniture d’API REST pour le frontend.
- Utilisation d’un volume pour persister le cache.

### 3. Frontend (Flask)
- Conteneur : `frontend_flask`
- Port exposé : `5000`
- Rôles :
  - Interface utilisateur pour l’inscription et la connexion.
  - Vérifications côté client (redondance, entropie, etc.).
  - Communication avec le backend via API REST.

---

## Qu’est-ce qu’un Bloom Filter ?

Un **Bloom Filter** est une structure de données probabiliste qui permet de tester rapidement si un élément (par exemple un mot de passe) appartient à un ensemble.

### Caractéristiques principales

- **Vérification ultra-rapide** : un test d’appartenance est beaucoup plus efficace qu’une recherche classique dans un fichier de plusieurs millions de lignes (_ex. : rockyou.txt_).
- **Pas de faux négatifs** : si le filtre indique que l’élément n’est pas présent, on est sûr qu’il n’y est pas.
- **Possibilité de faux positifs** : le filtre peut parfois indiquer qu’un élément est présent alors qu’il ne l’est pas vraiment (en fonction du taux de faux positifs choisi, ici **1%**).
- **Mémoire optimisée** : au lieu de stocker toute la liste (qui peut faire plusieurs centaines de Mo), on stocke un tableau de bits compact.

### Fonctionnement simplifié

1. Lors de la construction, chaque mot de passe de la wordlist est inséré dans le filtre à l’aide de plusieurs fonctions de hachage.
2. Pour vérifier un mot de passe, on applique les mêmes hachages et on teste les positions correspondantes dans le tableau de bits :
   - Si toutes les positions sont à 1 → le mot de passe est **probablement dans la wordlist**.
   - Si au moins une position est à 0 → le mot de passe est **certainement absent**.

---

## Bloom Filter et fichier de cache

Le fichier _rockyou.txt_ contient plus de **14 millions de mots de passe compromis**, ce qui le rend très coûteux à charger et à parcourir directement à chaque requête.

Pour optimiser les performances :

- Le backend construit un **Bloom Filter** à partir de _rockyou.txt_ (via l’endpoint `/bloom/cache`).
- Ce filtre est ensuite **sauvegardé sur disque** dans un fichier JSON (`cache/bloom.json`).
- Lors des redémarrages, le backend recharge automatiquement ce cache en mémoire au lieu de tout recalculer.
- Les vérifications de mot de passe se font ensuite via l’endpoint `/bloom/check?word=...` en temps quasi-constant.

Cela permet de rendre la vérification des mots de passe **rapide, scalable et peu coûteuse en mémoire**, tout en restant suffisamment fiable.

Vidéo explicative : https://www.youtube.com/watch?v=V3pzxngeLqw

## Mise en place

Pour lancer le projet, il suffit de se placer dans le répertoire racine qui contient à la fois le frontend et le backend, puis d’exécuter la commande suivante :

```docker compose up --build```

Cette commande permet de construire les images Docker et de démarrer simultanément tous les services définis dans le fichier docker-compose.yml (base de données PostgreSQL, backend Node.js/TypeScript et frontend Flask). Ainsi, l’environnement complet de développement est prêt à être utilisé sans configuration manuelle supplémentaire.

Arboressance : 

```
.
├── docker-compose.yml
├── README.md
├── SecureRegisterWebsiteBack/   # Projet backend (Node.js + TypeScript)
└── SecureRegisterWebsiteFront/  # Projet frontend (Flask)
```