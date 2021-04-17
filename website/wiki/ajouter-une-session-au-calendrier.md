title: ajouter une session au calendrier
order: 02
summary: Cette page détaille la marche à suivre afin d'ajouter votre nouvelle session au calendrier partagé du serveur.

## Ajouter une nouvelle session

### Créer un nouvel événement

Pour créer un nouvel événement dans le calendrier, allez dans le salon **#commands** de la secion **La Confrérie des GMs**, et tapez la commande suivante  en remplaçant `<event-name>` par le nom de votre partie.

```
!event create <event-name>
```

Cette commande va créer un événement, **sans l'enregistrer**. Vous devez d'abord ajouter les détails de l'événement via les commandes suivantes :
- `!event start ‹yyyy/MM/dd-HH:mm:ss›` permet de définir la date et l'heure de début de l'événement.
- `!event end ‹yyyy/MM/dd-HH:mm:ss›` permet de définir la date et l'heure de fin
- `!event description ‹description›` permet de saisir la description de l'événement. Merci d'y préciser **le nom du GM** et le **Système de jeu**.

Les commandes suivantes sont facultatives :
- `!event recur true` permet de rendre la session récurrente
- `!event freq ‹frequence›` permet de choisir la fréquence de cette récurrence. Les valeurs possibles sont : *DAILY* pour du quotidien, *WEEKLY* pour de l'hebdomadaire, *MONTHLY* pour du mensurel...
- `!event count ‹nb-occur›` permet de préciser le nombre d'occurences. Par exemple si <nboccur> vaut 2 et que la fréquence est WEEKLY, il y aura 2 événements créés à une semaine d'intervalle

Après chaque commande, le bot va vous renvoyer un aperçu de l'événement, vous pouvez répéter chaque commande pour modifier la valeur si vous vous êtes trompés.

### Enregistrer ou annuler

Vous pouvez enregistrer ou annuler l'événement en utilisant les commandes suivantes :
```
!event confirm
ou
!event cancel
```

## Modifier un événement

Vous pouvez modifier un événement déjà enregistrer en utilisant son identifiant *Event ID* que vous trouverez en bas du message posté par le bot à la confirmation.

```
!event edit <Event ID>
```

Vous pouvez ensuite suivre utiliser les commandes *start*, *stop* etc... pour modifier votre événement. **N'oubliez pas de terminer par un confirm ou un cancel**.


## Pour aller plus loin

La liste des commandes se trouve [ici](https://discalbot.com/commands). Veillez à n'utiliser que les commandes **!events**.
