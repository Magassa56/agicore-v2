# 3D / CNC — AGIcore-v2

> Domaine d'extension. Les modules CNC vivent dans `src/agicore/l5_action/cnc/` quand ils sont actifs.

---

## 1. Logiciels cibles

| Logiciel | Rôle |
|---|---|
| Fusion 360 | CAO paramétrique principale |
| FreeCAD | Alternative open source |
| OpenSCAD | Modélisation procédurale par script |

---

## 2. Formats de fichiers

| Format | Usage |
|---|---|
| STL | Maillage triangulé (impression 3D, échange) |
| STEP | Format CAO standard, paramétrique |
| G-code | Instructions machine CNC |

---

## 3. CNC

Pipeline cible :

```
[modèle CAO] → [toolpath generator] → [G-code] → [machine]
```

Optimisations attendues :
- minimisation des passes
- ordre d'usinage cohérent (ébauche → semi-finition → finition)
- gestion des outils (changement, profondeurs, vitesses)
- vérification anti-collision avant export

---

## 4. Librairies Python

| Lib | Usage |
|---|---|
| `trimesh` | Manipulation de maillages, opérations booléennes, export STL |
| `cadquery` | CAO paramétrique en Python — alternative scriptable à Fusion |
| `numpy-stl` | Lecture/écriture STL bas niveau |

---

## 5. Génération paramétrique

Objectif : exposer des designs comme des fonctions Python.

```python
def bracket(width: float, height: float, hole_diameter: float) -> Solid:
    ...
```

Avantages :
- versionnable dans Git
- testable
- composable (un design appelle d'autres designs)
- exportable en STL/STEP automatiquement

---

## 6. Interface machine

Communication possible :

| Mode | Méthode |
|---|---|
| Direct série | `pyserial` vers contrôleur GRBL / Marlin / autre |
| USB | Port virtuel série |
| Sender externe | Universal Gcode Sender, bCNC |

Toute commande directe machine doit passer par un connector L5 dédié, jamais en raw depuis L3/L4.

---

## 7. Sécurité physique

Règles dures avant tout envoi vers une machine réelle :

- vérification G-code par un linter (limites de course, vitesses, profondeurs)
- dry-run obligatoire avant première exécution
- bouton d'arrêt physique accessible
- log de chaque G-code envoyé, avec timestamp et machine_id
