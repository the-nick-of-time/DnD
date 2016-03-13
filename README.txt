 ____       ____     ____        ______                ___             
/\  _`\   /|  _ \   /\  _`\     /\__  _\              /\_ \            
\ \ \/\ \ |/\   |   \ \ \/\ \   \/_/\ \/   ___     ___\//\ \     ____  
 \ \ \ \ \ \// __`\/\\ \ \ \ \     \ \ \  / __`\  / __`\\ \ \   /',__\ 
  \ \ \_\ \/|  \L>  <_\ \ \_\ \     \ \ \/\ \L\ \/\ \L\ \\_\ \_/\__, `\
   \ \____/| \_____/\/ \ \____/      \ \_\ \____/\ \____//\____\/\____/
    \/___/  \/____/\/   \/___/        \/_/\/___/  \/___/ \/____/\/___/ 
		

Direct all comments, suggestions, and bug reports at github.com/the-nick-of-time
All tools in this package are released under the GNU General Public License version 2, as detailed within the file LICENSE. Refer to that document before doing anything except downloading for personal use.
These were written in Python 3.4.0 and I do not guarantee that they will work correctly on any other platform.

============================================================================================
SECTION 1: GENERAL USE

	1.1: Rolling
	Any string that can be parsed by the "rolling" code is called throughout all my related code a "rollable string". These are similar to arithmetic expressions, just with the d, h, and l operators added.
	The definitions of these operators are as follows:
	xdy rolls x y-sided dice and returns a sorted list of these rolls. xd[a,b,c,...] rolls x dice with sides a,b,c....
	xdyhz rolls x y-sided dice and returns the z highest of these rolls. This allows you to have advantage on rolls.
	xdylz rolls x y-sided dice and returns the z lowest of these rolls. This enables disadvantage.

	Examples of rollable strings:
	+4 									(positive four)
	-2 									(negative two)
	1d6 								(roll a six-sided die with sides numbered one through six)
	-1d6								(roll a d6 and take the negative)
	3d6+2								(roll 3d6 and add 2 to the sum)
	1d6+1d4+1						(roll a d6, add to it a d4, and add one to that)
	2d20h1+3+2					(roll 2d20, take the higher of the two rolls, add a total of five to it)
	3d6/2								(roll 3d6, divide the sum by 2; note that this returns an unrounded number)
	Less applicable functionalities:
	1d6^2 							(roll a d6, square the result)
	1d6^1d4							(roll a d6, raise it to a random power between 1 and 4)
	1d4d4d4							(roll a d4, roll that many d4s, sum them and roll that many d4s)
	1d[0,0,0,1,1,2]			(roll a six-sided die with three sides being 0, two 1, and one 2)
	1d[.5,.33,.25,.20]	(roll a four-sided die with sides 0.5, 0.33, 0.25, and 0.2)
	2d[1/2,1/3,1/4,1/5]	(roll two of the above without rounding)
	1d100>11						(roll a d100 and check whether the roll is greater than 11; displays a 1 for true and 0 for false)
	3d4%5								(roll 3d4, return the remainder after division by 5)

============================================================================================
SECTION 2: DICE
This program uses the rolling code to power a minimal interface for rolling dice. All you need to do is start it up from the main program and type in the box. The button or the enter key will roll the dice that you specify in the entry.


============================================================================================
SECTION 3: PLAYERS
Before getting to the fun part, you need to create your character file. This is done by starting up the character creator from the main program and filling it out as described below.
After finishing that, run the main program again and you're ready to go!
From here on out, you should not have to touch the character creator again until you gain a new attack.


	3.1: Character Creator
	This program will write a file called "*the name of your character*.ini" that contains all the information necessary to construct your character.
	
	Fill out the fields on the left and in the abilities section. These are largely self-explanatory. Class accepts the names of the classes in the Player's Handbook as well as "multiclass". This option is only used to determine the spell slots available to you, so if none of these options directly apply to you (Eldritch Knight maybe? I've never played one) use an equivalent class like Paladin.
    
	Next, fill out weapon and spell creation sections. Leave sections blank to use default values.
			
	Name: The name of the weapon or spell (not case-sensitive)
	
	Damage Dice: base damage done by the attack, like 1d4 or 2d10+6
	
	Ability used: str, dex, con, int, wis, or cha, the ability used with this attack (often class-dependent, but you need to put it in here)
	
	Attacks per Action: how many individual attacks are done with every attack action that you take. For instance, the spell Scorching Ray has a 3 for this entry. For AoE spells, you probably just want to put as many targets as could reasonably be hit by it. You can always just roll extra to make up the difference.
	
	Magic Bonus (Weapon): A magic bonus to be added to attack and damage rolls.
	
	Make Attack Roll?: If yes, do an attack roll with each attack. If no, it means that the attack automatically hits (for weapon) or instead requires a saving throw (spell).
	
	Saving Throw Type (spell): What save type the target needs to make (like Dexterity or Constitution)
	
	Ammunition (Weapon): Number of pieces of ammunition that the weapon has. One piece is consumed by each use of this weapon.
	
	Add Ability Modifier to Damage (spell): Whether to add your ability mod to the damage done by this spell. This is yes or no like the attack roll question.
	
	Spell Level: The level of the spell.
	
	Additional Information: This is space for some additional notes on the attack, to be displayed when you attack.

	After filling out one of these sections, press the associated "Make" button to commit this change to memory.
	When you want to save, hit the "Write" button. When you are done and want to quit, hit the "Quit" button.

	To edit one of the spell or weapon entries during the same session, fill out the section with the correct information and hit the "Make" button. When you create an entry that has the same name as another, it will overwrite the old entry.

	If editing later, you will want to use the "Read" button after entering your character's name to reopen the file. Otherwise, the old data will be discarded entirely. This also allows you to overwrite individual entries as if it was in the same session as you made it.
	
	
	
	3.2: Character Manager
	To use this program, enter the character's name in the relevant entry exactly as it appears in the title of the .ini file, then hit Enter or press the load button. This should set everything up for you.

	HP SECTION:
    This has several entries in it. You generally don't need to directly change any of them except for the bottom one.
    The bottom entry is where you put changes in your HP. It can be any valid rollable string, as defined in the rolling module. Upon pressing the "Alter HP" button, the value in the box is added to your current HP. Do note that, to take damage, you need enter a negative value in the box, like -4 or -3d6.

	ATTACK SECTION:
    To perform attacks, enter the name of the attack (not case-sensitive) into the box and then press the ATTACK button or the Enter key.
    The check boxes to the right of the main entry allow you to indicate whether you are making the attack with advantage or disadvantage. If both are checked, they cancel out.
    The attack and damage bonus entries below the main one are there to indicate special bonuses, beyond what is expected. Normally, your attack bonus will be equal to your ability modifier + your proficiency bonus + magic bonus on your weapon (if any). Your normal damage bonus is your ability modifier (for a weapon or a spell with the addAbilityToDamage property.) The two bonuses entered in these boxes can be any rollable string. For instance, if you have a support-heavy group, you could have a +1 on attack rolls and a +1d6+1 on damage. These sort of temporary buffs are what these entries are for.

	SPELL SECTION:
    This shows what spell slots you have not yet spent.
    When you cast a spell as an attack, this section will respond. For all your other spellcasting needs, there are the associated buttons. The + and - buttons regain or spend spell slots of that level. The Reset button refreshes your spell slots to the maximum, like when you rest and regain all expended spell slots.
    Note that this has no way of keeping track of sorcery points, ki points, or channel divinity uses. I leave that to you.

	GENERIC ROLL SECTION:
    This entry accepts any rollable string, and rolls it when you press the button.

	QUIT:
    Saves and quits. This saves all HP-related numbers, your current level, and even all of your abilities (in case those change at all).

		
============================================================================================
SECTION 4: DUNGEON MASTERS
The Monster Manager is written for you. It keeps track of monsters and allows you to roll any other dice you need while running a combat. There is no preparation needed to use this, so just run it as is.

	4.1: Using the Monster Manager
	The first thing you will likely want to do is press the "New Monster" button to open the dialog. This will create a popup window with a variety of fields that can be filled out. Fill them with relevant information and hit the "Finish" button.

	The main window will now contain a section that contains relevant information about the monster. From here, you can make the monster take damage (by inserting a negative value in the "Change HP" entry and pressing the button), recover HP (same but positive), or perform attacks. This aspect perhaps bears explanation. To perform an attack, fill out the attack bonus and damage done and press the button. The attack bonus is **added to the d20 roll and should not include the d20**, and can be any valid rollable string, as defined in section 1.1. 

	If you need to roll dice for any other reason, there is a section that has just an entry and a button.

	I recommend creating all the monsters first and then the characters. This ensures that the copy feature works correctly. However, it won't break anything if you add monsters after characters.
