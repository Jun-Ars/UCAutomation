-attained service now test access for API calling


-When creating a new sandbox, be sure to:
1. Create the following trunks:
   1. Centralized-SIP-Trunk-RG
   2. <name>-GW
   3. Markham-GW-Trunk
2. add local route group names: [911 Primary, 911 Secondary, PSTN Primary, PSTN Secondary]
3. add the following CSS: 'Incoming-ANI-E164-CSS'
4. add the following RG: 'Centralized-SIP-Trunk-RG'
5. Add the following CMG: 'Residence-CMG'
6. Add the following MRGL: 'Hub-MRGL'

-Things to fix:
1. Some Route Groups are named with the full home name rather than the shortened form, e.g.: 
   1. "Avondale-RG" as opposed to "Avondl-RG", the remaining are:
      1. Guildwood
      2. Kamloops
      3. Lakeshore
      4. Meadowbrook
      5. Montgomery
      6. Oak-Park
      7. Robert-Speck
      8. Royal-Gordon
      9. Clair-Hills
   2. "Cresga-RG" is named with the shortened form (as expected), the remaining correct ones are:
      1. Lansin
      2. Pemher
      3. Ridgep
      4. TRACAR (although this one is all caps for some reason)
      5. Vrives
2. There are 2 Residence Call Manager Groups, the second one contains only Villa Rive Sud
   1. Should this contain ALL Quebec Device Pools? How can we differentiate which DP belongs to each CMG?