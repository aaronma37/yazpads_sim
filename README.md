### Yazpad's warlock simulation

Gearsheet for this simulation can be found ~

The purpose of this simulation is to try to recover probabilistic properties of boss encounters.  

# Feature
DPS and stat weights with respect to percentiles in fights.  This gives insight on how to get maximum dps
parse given several attempts

Gear comparisons

Spec comparisons (see spec details below)

Dps vs. time



# Overall assumptions: 
Talisman of ephemeral power always on (work in progress to change)
curse of shadows always on


## Specs

# DS/RUIN w/Corruption
Rotation priority: Corrupion > Shadowbolt; Always lifetap if the warlock doesn't have mana for the prioritized action 

# DS/RUIN wo/Corruption
Rotation priority: Shadowbolt; Always lifetap if the warlock doesn't have mana for the prioritized action 

# SM/RUIN w/Corruption
Rotation priority: Corrupion > Shadowbolt; Always lifetap if the warlock doesn't have mana for the prioritized action 

# SM/RUIN w/Imp
Rotation priority: Corrupion > Shadowbolt; Always lifetap if the warlock doesn't have mana for the prioritized action 
Imp rotation:  Always cast firebolt

# MD/RUIN wo/Corruption
(work in progress)
Assumptions:  Always use succubus, the black book is active from 0 to 25 seconds
Succubus rotation: Always autoattack, always cast lash of pain (sniping coming soon)

## Instructions for running simulation
Modify spec in main.py
vim main.py

Run in parallel (may take a couple hours)
parallel --bar 'python3 main.py' ::: $(sec 10)

Modify spec in regression.py
vim regression.py

Run regression.py
python3 regression.py

The coefficients for uploading to google sheets should be in 
/yazpads_sim/<spec>/coeff/coef_.csv
  
## TODO
Fix google sheets rounding errors
Finish adding coeff for smaller increments in distributions
Debug MD/RUIN succubus
Implement lash sniping for succubus (only cast lash of pain when ISB is down)
Implement ISB uptime via composition of warlocks in raid as opposed to single lock (gives better estimate of crit/sp)

## Changelog 
03/28/2020
  Added MD/RUIN
  Decided to switch to increments of 5% for percentiles
  Added probability density functions, cumulative density functions on PDF tab
  Added mana potion/dark rune checkboxes
  
