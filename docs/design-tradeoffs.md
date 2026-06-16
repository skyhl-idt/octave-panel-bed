## McNeill, Matthew
*Tuesday, March 31, 2026 8:25 PM*

I recommend we move forward with Option 4.

  *   The amount of extra work to build the additional files will be relatively small
  *   It’s the most robust – no chance they can re-amplify from the same source material to build the same panel twice
  *   While changing handles would be nice, it seems unlikely to affect panel performance – if this is critical, we could add this complexity at the cost of increased risk of human error matching panels back up across sets during analysis.

Please let me know yay/nay on the selection

Option 1:

  *   Two sets of 200 panels with exactly the same content (call them design set 1 and 2) and a third where we scramble probes within panels, but keep the panel names the same
  *   Pro:

     *   Easiest organization
     *   No bed file changes – low likelihood of an analysis mix-up

  *   Con:

     *   Easiest to “fool” because sets 1 and 2 could be re-amplifications of the same material

Option 2:

  *   One set of original 200 panels, one set of scrambled probes within the original panels, one set of probes scrambled across panels.
  *   Pro:

     *   Tests both dimensions – Mix-up of probe positions in file & scramble across panels
     *   Scrambled panel is impossible to duplicate by pulling another lot

  *   Con:

     *   No historical comparison for the scrambled panels
     *   Some possibility to mix up panel names in the across-panel scrambled version, but this is mitigated if we just name the panels something new

Option 3:

  *   One set of original 200 panels, one set of scrambled probes within original panels, one set of the same original panels, but 10 probes are missing from each panel as a marker
  *   Pro:

     *   Simple design, similar to option 1 – low likelihood of a mix-up
     *   Allows for testing both the repositioning of the probes within the source file and it will be exceptionally difficult to make a panel with and without 10 probes
     *   The panels without the 10 probes could still be directly compared (in terms of probe concentration) to the ones with the 10 probes

  *   Con:

     *   It is possible to fake a panel with and without 10 probes and then spike those probes back in

Option 4:

  *   One set of original 200 panels, one set of the same original panels, but 10 probes are missing from each panel as a marker, and one set of probes scrambled across panels
  *   Pro:

     *   Has all of the variations from Options 2 and 3, making panel diversity the highest of the options
     *   Allows for testing both the repositioning of the probes within the source file and it will be exceptionally difficult to make a panel with and without 10 probes
     *   The panels without the 10 probes could still be directly compared (in terms of probe concentration) to the ones with the 10 probes

  *   Con:

     *   Most complex design, meaning increased chance to make a mistake (seems like a small chance so long as we send separate files)
     *   It is possible to fake a panel with and without 10 probes and then spike those probes back in, but even this chance it mitigated by having the fully scrambled set
     *   No historical comparison for the scrambled panels

---

## Kurihara, Laurie
*Wednesday, April 1, 2026 1:43 PM*

Are we planning the 80 libraries to test panels in the same positions as our original MRD 200 panel test (I think we tested 120 panels)? We will need to if we want to reference back to first MRD200 experiment, or do we need to query new chip positions and panels???

We are talking about scrambling probes within a panel to change their position, that's pretty subtle, wouldn't a better test be to move the entire panel location around the checkerboard to scramble the chip position of the SAME panels and see if that impacts reproducibility? It may also change PCR-handles if we swap black for white and panel order within, or we could hold that constant, where black stays on black, white stays on white in the same panel order per square.

If we scramble the probes across panels, I don't know how to interpret those results, as Matt indicated there would be no comparison set...

I like Option 4 that addresses Demaris concern best but adding a couple more options:

Chip 1:  Novel synthesis of original set

original MRD200 set, in original positions and PCR-handles, but leave the last 10 probes out for each panel (to prove new synthesis for Demaris)

Chip 2:  Swap the Black and White square positions, keeping all information within a square the same

original MRD200 set -10 last probes to match chip 1, but move panel sets of 10 on each checkerboard square together and significantly change its synthesis location (I expect if there are positional effects they will be more pronounced across the chip vs changing spots within the same panel position on the chip, such as edge vs middle). Keep PCR handles and the order within the black or white square the same.

On this set, include a different 15 universal probes for within the chip comparison (to prove new synthesis for Demaris vs chip 1) or will this impact performance of the other probes? Is there another way to uniquely identify this chip?

Chip 3: original MRD200 set -10 last probes like chip 1 and 2, except now swap PCR handles and/or panel order within a black or white square. Once again, how can we uniquely identify this chip, a third set of 15 universal probes?

---

## Henck, Steven
*Wednesday, April 1, 2026 1:47 PM*

I guess I like Option 2 as it tests both types of scrambling. Option 4 does not have the scrambling within panels.

However, as I said, you all pick what you want.

Kind regards,

Steven

---

## McNeill, Matthew
*Wednesday, April 1, 2026 4:07 PM*

We have a lot of ways to do this 😊

With this test, we want to:

  *   Look at panel aggregate performance metrics to confirm the machine works
  *   Confirm that the manufactured panels are novel
  *   (Laurie/Matt) Look at panel synthesis reproducibility (edge vs central effects; might also be affected by position near gasket edge)

Confirm novel panels

  *   Confirm novel handles per panel (would require sequencing the probes directly)
  *   Scramble probes across panels
  *   Remove / add / replace some probes

@Henck, Steven: If we moved panels around in groups of 10 as Laurie suggest, would Octave help us with that positioning? Will Octave ship the manufactured panels to IDT upon completion? We could spot-check the panels by sequencing them if we wanted to later.

How about this:

  *   Chip 1: original design & panel naming, minus 10 probes in each panel, rename panels from prior study
  *   Chip 2: Same as chip 1, minus 5 additional probes in each panel, and shift panels by 10 positions and order in the design file. We’ll request amp primers used in same positions as chip 1. We’ll create unique panel names.
  *   Chip 3: Scramble probes across panels. For comparing probe synthesis performance to other chips and the prior study, we normalize probe relative coverage to the common 15 probes. This will also allow us to ask whether probe activity is probe-context dependent (eg, the other probes it is synthesized or captured with)

This approach means we don’t need to identify 15 new control probes 😊

---

## Henck, Steven
*Wednesday, April 1, 2026 4:27 PM*

Which panels we “randomly” select are up to us to decide. Whether we compare back to the original experiment is again up to us. If so, it is an experiment within the boundaries of what this test is supposed to do, so it is fine but not a requirement. Again, kind of a free experiment.

---

## Kurihara, Laurie
*Wednesday, April 1, 2026 7:13 PM*

I think we are very close!

Matt I think your final suggestion is good, we will guarantee new synthesis, see impact of chip positioning and context within panels-

Sounds like a win to me-

We just need to know how to scramble the squares...

---

## Henck, Steven
*Wednesday, April 1, 2026 7:44 PM*

If we moved panels around in groups of 10 as Laurie suggest, would Octave help us with that positioning? No thought goes into positioning. I believe they are going to put them in the order you submit in the file. We could probably guess what order vertical vs. horizontal, or I could ask if you want.

Will Octave ship the manufactured panels to IDT upon completion? That was not the plan. They are doing the testing in China to avoid the time lost to shipment / customs. I could ask that they send us the panels after the test, but they will arrive a month or more after the test.

We could spot-check the panels by sequencing them if we wanted to later. This would only be possible if we have them ship the panels to us.

By July or so, we should have a synthesizer in Sunnyvale and you can have Abe’s team run whatever experiments you want.

---

## McNeill, Matthew
*Thursday, April 2, 2026 6:42 AM*

We were able to get information back on positioning during our prior study.

Perhaps we re-use Bosun’s positioning diagram and communication tools and just make the request. We could adjust the panel position in the file to reflect the 10 position shift goal. Octave shared the panel position file with us in the last round.

If we can get the panels shipped to us, it’s a hedge if we later decide we have questions, but we may not do the testing. <- Is this low enough cost to be a reasonable request?

Does this sound reasonable?

---

## Henck, Steven
*Thursday, April 2, 2026 12:04 PM*

@Kurihara, Laurie do you have the PO or invoice from the Round 2 test panel shipment? That should give us a ballpark of the shipping cost. I wouldn’t think it would be more than $2-3k.

---

## Kurihara, Laurie
*Thursday, April 2, 2026 4:37 PM*

I'm only finding sales orders and invoices for Octave materials, sorry

---

## Kurihara, Laurie
*Thursday, April 2, 2026 4:58 PM*

I don't think so, but I can look

---

## McNeill, Matthew
*Monday, June 15th, 2026 11:22 AM*

Hi Soren,
 
Would you please create the relevant probe and target bed files to correspond to the three arrangements of probes? As you can see from the set descriptions on 4/1, we’ll also want to confirm that no extra probes were included in the synthesis. For the kinds of analyses we previous did, please see reports 2-4 here: TST Support. Jing should also be able to help.
 
I sent you the created probe sets in a Teams message (too big for email).
You can find the original target and probe bed files here: /mnt/archive/work/lren/projects/xGen/POTA/Design_200_Panels/Kyudo2_Panel_Files
 

