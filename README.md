# lilac-chaser

Implementation of Jeremy Hinton's Lilac Chaser optical illusion in pure Python for Stanford PSYCH30. Demonstrates three perceptual phenomena simultaneously: Troxler's fading, negative afterimages, and the phi phenomenon. When you stare at the cross you can see a green dot chase around the circle. I wanted interactive parameter control without the overhead of specialized graphics libraries. Contains buttons/sliders for speed, direction, dot colors, and background colors. All changes apply in real-time while the illusion runs. Tkinter handles everything fine!

## Usage

```bash
python lilac_chaser.py
```

That's it! No `pip install`.

## The science

The illusion exploits three neural mechanisms:
**Troxler's fading**: Stationary peripheral stimuli fade due to retinal and cortical adaptation. 
**Opponent color processing**: Lilac stimulates L+S cones while suppressing M cones. When removed, the M pathway rebounds, producing green afterimages through opponent channel rebalancing.
**Phi phenomenon**: Sequential afterimage presentation creates apparent motion via V1 direction-selective cells and V5/MT spatiotemporal integration. 

## Implementation notes

I used callback factories instead of lambda closures to avoid the classic Python late-binding gotcha that was making buttons unresponsive. The default 90ms timing hits the sweet spot for motion perception while allowing sufficient afterimage buildup. If you make it spin slow enough it becomes a whole other illusion of the dots jumping and moving (phi phenomenon). 
