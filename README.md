# Droppable
This is a basic paddle game where you catch the falling faces.<br>

# Project Objectives
This was created to begin working with spritesheets for custom animations. I also used this to develop a basic AI that will strategically play the game.<br>

# Features 
Two different monsters are dropped in randomly generate orders and locations from the top of the screen. The player has a movable paddle, along with two special power ups. An AI mode is available that can be switched on and off at any time. Current stats such as points, streak, and power up counters are displayed.<br>

# Display
Animations are drawn in Adobe Illustrator and pygame is used to handle the sprite sheets.<br>
[pygame](http://www.pygame.org/)<br>

# Controls
Left and Right Arrows: Move paddle<br>
Up Arrow: Toggle AI mode<br>
1: Drop bomb<br>
2: Freeze enemies<br>

# AI Mode
When toggled on, the AI player will target the droppable that is the closest to the bottom, but is still able to be caught. It will not target a droppable that it will miss because the paddle won't be able to reach it in time. Due to droppables moving at different speeds, the AI will continously reevalute it's target to ensure it maximizes the amount of objects it catches. It will also use bombs when a certain amount of points are on the screen to be gathered.<br>

# Screenshots
<img src="http://betterin30days.github.io/droppable/screenshots/droppable1.png"/><br>
<img src="http://betterin30days.github.io/droppable/screenshots/droppable2.png"/><br>
<img src="http://betterin30days.github.io/droppable/screenshots/droppable3.png"/><br>