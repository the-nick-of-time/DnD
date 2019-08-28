```
 ____       ____     ____        ______                ___             
/\  _`\   /|  _ \   /\  _`\     /\__  _\              /\_ \            
\ \ \/\ \ |/\   |   \ \ \/\ \   \/_/\ \/   ___     ___\//\ \     ____  
 \ \ \ \ \ \// __`\/\\ \ \ \ \     \ \ \  / __`\  / __`\\ \ \   /',__\
  \ \ \_\ \/|  \L>  <_\ \ \_\ \     \ \ \/\ \L\ \/\ \L\ \\_\ \_/\__, `\
   \ \____/| \_____/\/ \ \____/      \ \_\ \____/\ \____//\____\/\____/
    \/___/  \/____/\/   \/___/        \/_/\/___/  \/___/ \/____/\/___/
```

Direct all comments, suggestions, and bug reports at github.com/the-nick-of-time
All tools in this package are released under the GNU General Public License version 2, as detailed within the file LICENSE. Refer to that document before doing anything except downloading for personal use.
These were written in Python 3.5.2 and I do not guarantee that they will work correctly on any other platform.


# GENERAL USE

## Rolling

| Operator | Format | Meaning |
| :------- | :----- | :------ |
| d        | *x*d*y*       | Take a *y*-sided die and roll *x* of them. *y* can be an integer, and works just as you would expect. It can also be a list of arbitrary numbers, in which case it works as a die with one side labeled with each number in the list.  |
| da | *x*da*y* | Take a *y*-sided die and return the average as if *x* of them had been rolled. This returns an unrounded number. |
| dc | *x*dc*y* | Roll a critical hit, where the number of dice rolled is doubled. |
| dm | *x*dm*y* | Roll the maximum on every die rolled. |
| h | *ROLL*h*n* | After making a roll, discard all but the highest *n* of the rolls. Hint: 2d20h1 is advantage. |
| l | *ROLL*l*n* | After making a roll, discard all but the lowest *n* of the rolls. Hint: 2d20l1 is disadvantage. |
| f | *ROLL*f*n* | After making a roll, treat any value that is less than *n* as *n*. |
| c | *ROLL*c*n* | After making a roll, treat any value that is greater than *n* as *n*. |
| ro | *ROLL*ro*n* | After making a roll, look at all of them and reroll any that are equal to *n*, reroll those, and take the result. |
| Ro | *ROLL*Ro*n* | After making a roll, look at all of them and reroll any that are equal to *n* and reroll those. If that number comes up again, continue rerolling until you get something different. |
| rh | *ROLL*rh*n* | After making a roll, look at all of them and reroll any that are strictly greater than *n*, reroll those, and take the result. |
| Rh | *ROLL*Rh*n* | After making a roll, look at all of them and reroll any that are greater than *n* and reroll those. If a number greater than *n* comes up again, continue rerolling until you get something different. |
| rl | *ROLL*rl*n* | After making a roll, look at all of them and reroll any that are strictly less than *n*, reroll those, and take the result. |
| Rl | *ROLL*Rl*n* | After making a roll, look at all of them and reroll any that are less than *n* and reroll those. If a number less than *n* comes up again, continue rerolling until you get something different. |
| ^ | *x*^*y* | Raise *x* to the *y* power. |
| \* | *x*\**y* | *x* times *y*. |
| / | *x*/*y* | *x* divided by *y*. This returns an unrounded number. |
| % | *x*%*y* | *x* modulo *y*. |
| + | *x*+*y* | *x* plus *y*. |
| - | *x*-*y* | *x* minus *y*. |
| > | *x*>*y* | Check if *x* is greater than *y*. Returns a 1 for yes and 0 for no. |
| >= | *x*>=*y* | Check if *x* is greater than or equal to *y*. Returns a 1 for yes and 0 for no. |
| < | *x*<*y* | Check if *x* is less than *y*. Returns a 1 for yes and 0 for no. |
| <= | *x*<=*y* | Check if *x* is less than or equal to *y*. Returns a 1 for yes and 0 for no. |
| = | *x*=*y* | Check if *x* is equal to *y*. Returns a 1 for yes and 0 for no. |
| & | *x*&*y* | Check if *x* and *y* are both nonzero. |
| &#124; | *x*&#124;*y* | Check if at least one of *x* or *y* is nonzero. |

Any string that can be parsed by the "rolling" code is called throughout all my related code a "rollable string". These are similar to arithmetic expressions, just with some dice-specific operators added.

-----

# Using DnD.pyw

## Dice
This program uses the rolling code to power a minimal interface for rolling dice. All you need to do is start it up from the main program and type in the box. The button or the enter key will roll the dice that you specify in the entry.


-----
## Character Manager

### HP
The box in the lower left is where you enter rolls that will change your HP. For instance, if you take 1d8+3 damage from an arrow, you would enter -(1d8+3) and either hit Enter or press the "Change HP" button. If you instead gain some temporary hit points, press the "Add Temp HP" button. For instance, if you cast *false life* you could enter 1d4+4 then press the "Add Temp HP" button.

### Abilities and Skills
Here you can make ability checks, saving throws, and skill checks. The saves and skills you are proficient in are highlighted in green. Whether you have advantage or disadvantage on this roll is controlled by the checkboxes at the bottom.

### Basic Roller
There are a couple of these throughout the interface. Here, you can place any arbitrary roll to make. In addition to all of the stuff described earlier, you can use variables from your character by including them in the form `$var` where `var` can be:

| `var` | Meaning |
| :------------- | :------------- |
| `proficiency` | Your proficiency bonus |
| `ability_mod` | Where ability is any ability name or its short version; gets that modifier |
| `level` | Your total level |
| `caster_level` | Your total caster level |
| `class_level` | Your level in a specific class |
<!-- | `str_mod` | Your Strength modifier |
| `dex_mod` | Your Dexterity modifier |
| `con_mod` | Your Constitution modifier |
| `int_mod` | Your Intelligence modifier |
| `wis_mod` | Your Wisdom modifier |
| `cha_mod` | Your Charisma modifier | -->

### Attacks
SUBJECT TO CHANGE

### Conditions
Toggle conditions using the buttons. All the effects are printed below the rank of buttons.

### Class and Racial Features
Their names are displayed alongside a button that leads to their full description.

### Resources
All resources you have available are listed here. When you use one (with the '-' button) its value is rolled and displayed in the lower left. When you rest (using either of the buttons at the bottom of the screen) the numbers are reset. You could also manually reset them with the button associated with that resource.

### Inventory
Displays all your items categorized into weapons, apparel, treasure, and generic items. It keeps track of their weight and uses the variant encumbrance rules (PHB 176) to calculate any penalties you might have for carrying so much.

### Spells
Shows all the spells you have prepared. You can view a detailed description of each spell with the '?' button, or cast it with the "Cast" button. There is another roller here so you can roll any dice associated with the spell.  
Spell slots are shown on the right. You can manually change each number with the buttons or by typing a new number in the box.

----------
## Monster Manager
In the beginning, there is a simple dice roller. It has the functionality described at the beginning.

When you press the "New Monster" button, you get a popup. You can either press "Load from file" or fill out the data yourself.
