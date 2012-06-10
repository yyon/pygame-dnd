from gui import * #@UnusedWildImport
import functools
import data
import dungeonmap

entitytypes = ["npc"]

skills = [["appraise", "int"], ["autohypnosis", "wis"], ["balance", "dex"], ["bluff", "cha"], ["climb", "str"], ["concentration", "con"], ["craft", "int"], ["decipher script", "int"], ["diplomacy", "cha"], ["disable device", "int"], ["disguise", "cha"], ["escape artist", "dex"], ["forgery", "int"], ["gather information", "cha"], ["handle animal", "cha"], ["heal", "wis"], ["hide", "dex"], ["intimidate", "cha"], ["jump", "str"], ["knowledge (arcana)", "int"], ["knowledge (arch/eng)", "int"], ["knowledge (dungeoneering)", "int"], ["knowledge (geography)", "int"], ["knowledge (history)", "int"], ["knowledge (local)", "int"], ["knowledge (nature)", "int"], ["knowledge (nobility)", "int"], ["knowledge (planes)", "int"], ["knowledge (psionics)", "int"], ["knowledge (religion)", "int"], ["listen", "wis"], ["move silently", "dex"], ["open lock", "dex"], ["perform (act)", "cha"], ["perform (comedy)", "cha"], ["perform (dance)", "cha"], ["perform (keyboard)", "cha"], ["perform (oratory)", "cha"], ["perform (percussion)", "cha"], ["perform (string instrument)", "cha"], ["perform (wing instrument)", "cha"], ["perform (sing)", "cha"], ["profession", "wis"], ["psicraft", "int"], ["ride", "dex"], ["search", "int"], ["sense motive", "wis"], ["sleight of hand", "dex"], ["spellcraft", "int"], ["spot", "wis"], ["survival", "wis"], ["swim", "str"], ["tumble", "dex"], ["use magic device", "cha"], ["use psionic device", "cha"], ["use rope", "dex"]]

class entitytypeselector(Window):
	def __init__(self, method):
		Window.__init__(self, "Entity Type", scrollbar=True)
		
		self.method = method
		
		self.refreshentities()
		
	def refreshentities(self):
		for entitytype in entitytypes:
			b = button(self, entitytype, functools.partial(self.selectentitytype, entitytype))
			self.pack(b)
			
	def selectentitytype(self, entity):
		self.close()
		self.method(entity)

class editor(Window):
	def __init__(self, title, width, height, scrollbar=True):
		Window.__init__(self, title, width, height, scrollbar=scrollbar)
		self.dataitems = {}

	def function(self, function, arguments, result):
		for control in arguments:
			control.changemethod.append(functools.partial(self.runfunction, function, arguments, result))
		
	def runfunction(self, function, arguments, result):
		try:
			self.setcontroldata(result, function(*[self.getcontroldata(control) for control in arguments]))
			for method in result.changemethod:
				method()
		except:
			pass
	
	def getcontroldata(self, control):
		if isinstance(control, (entry)):
			return control.text
		elif isinstance(control, (checkbox)):
			return control.checked
		elif isinstance(control, (listbox)):
			return control.items
	
	def setcontroldata(self, control, value):
		if isinstance(control, (entry)):
			control.text = value
			control.rendertext()
		elif isinstance(control, (checkbox)):
			control.checked = value
		elif isinstance(control, (listbox)):
			if not isinstance(value, (list)):
				value = [value]
			control.items = value
			control.refreshitems()
	
	def link(self, control, variable, default):
		self.dataitems[variable] = control
		self.setcontroldata(control, self.database.get(variable, default))
		
	def close(self):
		for variable in self.dataitems:
			control = self.dataitems[variable]
			self.database.set(variable, self.getcontroldata(control))
			
		self.database.write()
		
		Window.close(self)

class npceditor(editor):
	def __init__(self, entity, entitieswindow):
		editor.__init__(self, entity, width=500, height=500, scrollbar=True)
		
		self.entity = entity
		self.entitieswindow = entitieswindow
		
		self.database = data.database("entities", self.entity)
		
		largefontsize = 20
		numboxwidth = 20
		
		abilitywidth = 30

		# Images
		
		self.imgdrawer = drawer(self, "Images")
		
		self.imgdrawer.pack(label(self, "icon"))
		
		icon = picturebox(self, os.path.join(dungeonmap.entityimgfolder, entity), "icon.png", size=dungeonmap.actualentitysize)
		self.imgdrawer.pack(icon)
		
		self.imgdrawer.pack(label(self, "view from front"))
		
		front = picturebox(self, os.path.join(dungeonmap.entityimgfolder, entity), "front.png", size=dungeonmap.actualentitysize)
		self.imgdrawer.pack(front)
		
		self.imgdrawer.pack(label(self, "view from back"))
		
		back = picturebox(self, os.path.join(dungeonmap.entityimgfolder, entity), "back.png", size=dungeonmap.actualentitysize)
		self.imgdrawer.pack(back)
		
		self.imgdrawer.pack(label(self, "view from left"))
		
		left = picturebox(self, os.path.join(dungeonmap.entityimgfolder, entity), "left.png", size=dungeonmap.actualentitysize)
		self.imgdrawer.pack(left)
		
		self.imgdrawer.pack(label(self, "view from right"))
		
		right = picturebox(self, os.path.join(dungeonmap.entityimgfolder, entity), "right.png", size=dungeonmap.actualentitysize)
		self.imgdrawer.pack(right)
		
		self.pack(self.imgdrawer)
		
		# Details
		
		self.detailsdrawer = drawer(self, "Details")
		
		l = label(self, "full name: ")
		self.detailsdrawer.pack(l)

		name = entry(self, 100)
		self.detailsdrawer.pack(name)
		self.link(name, "fullname", entity)
		
		l = label(self, "class: ")
		self.detailsdrawer.pack(l)
		
		classentry = entry(self, 100)
		self.detailsdrawer.pack(classentry)
		self.link(classentry, "class", "")
		
		l = label(self, "level: ")
		self.detailsdrawer.pack(l)
		
		lvl = entry(self, 50, numbers=True)
		self.detailsdrawer.pack(lvl)
		self.link(lvl, "level", "0")
		
		l = label(self, "race: ")
		self.detailsdrawer.pack(l)
		
		race = entry(self, 100)
		self.detailsdrawer.pack(race)
		self.link(race, "race", "")
		
		l = label(self, "alignment: ")
		self.detailsdrawer.pack(l)
		
		alignment = entry(self, 100)
		self.detailsdrawer.pack(alignment)
		self.link(alignment, "alignment", "")

		self.pack(self.detailsdrawer)
		
		# Hit Points
		
		self.hpdrawer = drawer(self, "Hit Points")
		
		l = label(self, "total hp: ")
		l.width = 50
		self.hpdrawer.pack(l)
		
		hp = entry(self, numboxwidth, numbers=True)
		self.hpdrawer.pack(hp, "right")
		self.link(hp, "hit points", "0")
		
		self.pack(self.hpdrawer)
		
		# Abilities
		
		self.abilitydrawer = drawer(self, "Ability Scores")
		
		l = label(self, "")
		l.width = 20
		self.abilitydrawer.pack(l)
		
		l = label(self, "score")
		l.width = abilitywidth
		self.abilitydrawer.pack(l, "right")
		
		l = label(self, "base")
		l.width = abilitywidth
		self.abilitydrawer.pack(l, "right")
		
		l = label(self, "race")
		l.width = abilitywidth
		self.abilitydrawer.pack(l, "right")
		
		l = label(self, "magic")
		l.width = abilitywidth
		self.abilitydrawer.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.abilitydrawer.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.abilitydrawer.pack(l, "right")
		
		l = label(self, "modifier")
		l.width = abilitywidth
		self.abilitydrawer.pack(l, "right")
		
		saveabilities = {}
		self.abilitymodifiers = {}
		
		for ability in ["str","dex","con","int","wis","cha"]:
			abilitylabel = label(self, ability)
			abilitylabel.width = 20
			self.abilitydrawer.pack(abilitylabel)
			
			total = entry(self, numboxwidth, numbers=True)
			self.abilitydrawer.pack(total, "right")
			self.link(total, ability+" total", 10)
			
			self.abilitydrawer.pack(label(self, "="), "right")
			
			base = entry(self, numboxwidth, numbers=True)
			self.abilitydrawer.pack(base, "right")
			self.link(base, ability+" base", 10)
			
			self.abilitydrawer.pack(label(self, "+"), "right")
			
			race = entry(self, numboxwidth, numbers=True)
			self.abilitydrawer.pack(race, "right")
			self.link(race, ability+" race", 0)
			
			self.abilitydrawer.pack(label(self, "+"), "right")
			
			enhancement = entry(self, numboxwidth, numbers=True)
			self.abilitydrawer.pack(enhancement, "right")
			self.link(enhancement, ability+" enhancement", 0)
			
			self.abilitydrawer.pack(label(self, "+"), "right")
			
			miscplus = entry(self, numboxwidth, numbers=True)
			self.abilitydrawer.pack(miscplus, "right")
			self.link(miscplus, ability+" misc plus", 0)
			
			self.abilitydrawer.pack(label(self, "-"), "right")
			
			miscminus = entry(self, numboxwidth, numbers=True)
			self.abilitydrawer.pack(miscminus, "right")
			self.link(miscminus, ability+" misc minus", 0)
			
			self.abilitydrawer.pack(label(self, "|"), "right")
			
			modifier = entry(self, numboxwidth, numbers=True)
			self.abilitydrawer.pack(modifier, "right")
			self.link(modifier, ability+" modifier", 0)
			
			self.function(self.abilityscore, [base, race, enhancement, miscplus, miscminus], total)
			self.function(self.abilitymodifier, [total], modifier)
			
			self.abilitymodifiers[ability] = modifier
			if ability == "con":
				saveabilities["fort"] = modifier
			elif ability == "dex":
				saveabilities["ref"] = modifier
			elif ability == "wis":
				saveabilities["will"] = modifier
				
		self.pack(self.abilitydrawer)
		
		# Combat Options
		
		self.weaponsdrawer = drawer(self, "Combat Options")
		
		l = label(self, "base attack bonus: ")
		self.weaponsdrawer.pack(l)
		
		bab = entry(self, numboxwidth, numbers=True)
		self.weaponsdrawer.pack(bab, "right")
		self.link(bab, "base attack bonus", "0")

		l = label(self, "weapon")
		l.width = 100
		self.weaponsdrawer.pack(l)
		
		l = label(self, "attack")
		l.width = 40
		self.weaponsdrawer.pack(l, "right")
		
		l = label(self, "damage")
		l.width = 50
		self.weaponsdrawer.pack(l, "right")
		
		l = label(self, "crit")
		l.width = 50
		self.weaponsdrawer.pack(l, "right")
				
		for weapon in range(4):
			weaponname = entry(self, 100)
			self.weaponsdrawer.pack(weaponname)
			self.link(weaponname, "weapon "+str(weapon), "")
			
			attack = entry(self, 40, numbers=True)
			self.weaponsdrawer.pack(attack, "right")
			self.link(attack, "weapon attack "+str(weapon), 0)
			
			dmg = entry(self, 50)
			self.weaponsdrawer.pack(dmg, "right")
			self.link(dmg, "weapon damage "+str(weapon), "")
			
			crit = entry(self, 50)
			self.weaponsdrawer.pack(crit, "right")
			self.link(crit, "weapon crit "+str(weapon), "")
		
		self.pack(self.weaponsdrawer)
		
		# Speed
		
		self.speeddrawer = drawer(self, "Speed")
		
		l = label(self, "speed: ")
		l.width = 50
		self.speeddrawer.pack(l)
		
		speed = entry(self, 50, numbers=True)
		self.speeddrawer.pack(speed, "right")
		self.link(speed, "speed", "0")
		
		l = label(self, "initiative: ")
		l.width = 50
		self.speeddrawer.pack(l)
		
		init = entry(self, 50, numbers=True)
		self.speeddrawer.pack(init, "right")
		self.link(init, "initiative", "0")
		
		self.pack(self.speeddrawer)
		
		# Grapple
		
		self.grappledrawer = drawer(self, "Grapple")
		
		l = label(self, "grapple: ")
		l.width = 50
		self.grappledrawer.pack(l)
		
		grapple = entry(self, 50, numbers=True)
		self.grappledrawer.pack(grapple, "right")
		self.link(grapple, "grapple", "0")
		
		self.pack(self.grappledrawer)
		
		# Saving Throws
		
		self.savedrawer = drawer(self, "Saving Throws")
		
		l = label(self, "")
		l.width = 20
		self.savedrawer.pack(l)
		
		l = label(self, "total")
		l.width = abilitywidth
		self.savedrawer.pack(l, "right")
		
		l = label(self, "base")
		l.width = abilitywidth
		self.savedrawer.pack(l, "right")
		
		l = label(self, "ability")
		l.width = abilitywidth
		self.savedrawer.pack(l, "right")
		
		l = label(self, "magic")
		l.width = abilitywidth
		self.savedrawer.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.savedrawer.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.savedrawer.pack(l, "right")

		for save in ["fort", "ref", "will"]:
			abilitylabel = label(self, save)
			abilitylabel.width = 20
			self.savedrawer.pack(abilitylabel)
			
			total = entry(self, numboxwidth, numbers=True)
			self.savedrawer.pack(total, "right")
			self.link(total, save+" total", 0)
			
			self.savedrawer.pack(label(self, "="), "right")
			
			base = entry(self, numboxwidth, numbers=True)
			self.savedrawer.pack(base, "right")
			self.link(base, save+" base", 0)
			
			self.savedrawer.pack(label(self, "+"), "right")
			
			ability = entry(self, numboxwidth, numbers=True)
			self.savedrawer.pack(ability, "right")
			self.link(ability, save+" ability", 0)
					
			self.savedrawer.pack(label(self, "+"), "right")
			
			magic = entry(self, numboxwidth, numbers=True)
			self.savedrawer.pack(magic, "right")
			self.link(magic, save+" magic", 0)
			
			self.savedrawer.pack(label(self, "+"), "right")
			
			miscplus = entry(self, numboxwidth, numbers=True)
			self.savedrawer.pack(miscplus, "right")
			self.link(miscplus, save+" misc plus", 0)
					
			self.savedrawer.pack(label(self, "-"), "right")
			
			miscminus = entry(self, numboxwidth, numbers=True)
			self.savedrawer.pack(miscminus, "right")
			self.link(miscminus, save+" misc minus", 0)
			
			self.function(self.savescore, [base, ability, magic, miscplus, miscminus], total)
			self.function(self.same, [saveabilities[save]], ability)
			
		self.pack(self.savedrawer)
		
		# Armor
		
		self.armordrawer = drawer(self, "Armor")
		
		l = label(self, "total")
		l.width = abilitywidth
		self.armordrawer.pack(l)
		
		l = label(self, "")
		l.width = abilitywidth
		self.armordrawer.pack(l, "right")
		
		l = label(self, "armor")
		l.width = abilitywidth
		self.armordrawer.pack(l, "right")
		
		l = label(self, "shield")
		l.width = abilitywidth
		self.armordrawer.pack(l, "right")
		
		l = label(self, "dex")
		l.width = abilitywidth
		self.armordrawer.pack(l, "right")
		
		l = label(self, "size")
		l.width = abilitywidth
		self.armordrawer.pack(l, "right")
		
		l = label(self, "natrl")
		l.width = abilitywidth
		self.armordrawer.pack(l, "right")
		
		l = label(self, "deflect")
		l.width = abilitywidth
		self.armordrawer.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.armordrawer.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.armordrawer.pack(l, "right")
		
		total = entry(self, numboxwidth, numbers=True)
		self.armordrawer.pack(total)
		self.link(total, "AC total", 10)
		
		self.armordrawer.pack(label(self, "="), "right")
		
		l = label(self, "10")
		l.width = numboxwidth
		self.armordrawer.pack(l, "right")

		self.armordrawer.pack(label(self, "+"), "right")
		
		armor = entry(self, numboxwidth, numbers=True)
		self.armordrawer.pack(armor, "right")
		self.link(armor, "AC armor", 0)
		
		self.armordrawer.pack(label(self, "+"), "right")
				
		shield = entry(self, numboxwidth, numbers=True)
		self.armordrawer.pack(shield, "right")
		self.link(shield, "AC shield", 0)
		
		self.armordrawer.pack(label(self, "+"), "right")
				
		dex = entry(self, numboxwidth, numbers=True)
		self.armordrawer.pack(dex, "right")
		self.link(dex, "AC dex", 0)
		self.function(self.same, [self.abilitymodifiers["dex"]], dex)
		
		self.armordrawer.pack(label(self, "+"), "right")
				
		size = entry(self, numboxwidth, numbers=True)
		self.armordrawer.pack(size, "right")
		self.link(size, "AC size", 0)
		
		self.armordrawer.pack(label(self, "+"), "right")
				
		natural = entry(self, numboxwidth, numbers=True)
		self.armordrawer.pack(natural, "right")
		self.link(natural, "AC natural", 0)
		
		self.armordrawer.pack(label(self, "+"), "right")
				
		deflection = entry(self, numboxwidth, numbers=True)
		self.armordrawer.pack(deflection, "right")
		self.link(deflection, "AC deflection", 0)
		
		self.armordrawer.pack(label(self, "+"), "right")
		
		miscplus = entry(self, numboxwidth, numbers=True)
		self.armordrawer.pack(miscplus, "right")
		self.link(miscplus, "AC misc plus", 0)
		
		self.armordrawer.pack(label(self, "-"), "right")
				
		miscminus = entry(self, numboxwidth, numbers=True)
		self.armordrawer.pack(miscminus, "right")
		self.link(miscminus, "AC misc minus", 0)
		
		self.function(self.armorclass, [armor, shield, dex, size, natural, deflection, miscplus, miscminus], total)

		l = label(self, "touch: ")
		l.width = 50
		self.armordrawer.pack(l)
		
		touch = entry(self, 100, numbers=True)
		self.armordrawer.pack(touch, "right")
		self.link(touch, "AC touch", 10)
		
		self.function(self.toucharmorclass, [armor, shield, dex, size, natural, deflection, miscplus, miscminus], touch)
		
		l = label(self, "flat-footed: ")
		l.width = 50
		self.armordrawer.pack(l)
		
		flat = entry(self, 100, numbers=True)
		self.armordrawer.pack(flat, "right")
		self.link(flat, "AC flatfooted", 10)
		
		self.function(self.flatarmorclass, [armor, shield, dex, size, natural, deflection, miscplus, miscminus], flat)
		
		l = label(self, "")
		l.width = 50
		self.armordrawer.pack(l)
				
		l = label(self, "type")
		l.width = 100
		self.armordrawer.pack(l, "right")
				
		l = label(self, "max dex")
		l.width = 50
		self.armordrawer.pack(l, "right")
				
		l = label(self, "armor check")
		l.width = 70
		self.armordrawer.pack(l, "right")
				
		l = label(self, "weight")
		l.width = 50
		self.armordrawer.pack(l, "right")
		
		for armortype in ["armor", "shield"]:
			l = label(self, armortype)
			l.width = 50
			self.armordrawer.pack(l)
			
			nametype = entry(self, 100)
			self.armordrawer.pack(nametype, "right")
			self.link(nametype, armortype + " type", "")
			
			maxdex = entry(self, 50, numbers=True)
			self.armordrawer.pack(maxdex, "right")
			self.link(maxdex, armortype + " max dex", 0)
			
			acpenalty = entry(self, 70, numbers=True)
			self.armordrawer.pack(acpenalty, "right")
			self.link(acpenalty, armortype + " armor check penalty", 0)
			
			weight = entry(self, 50, numbers=True)
			self.armordrawer.pack(weight, "right")
			self.link(weight, armortype + " weight", 0)
		
		self.pack(self.armordrawer)
		
		# XP / Money
		
		self.moneydrawer = drawer(self, "XP / Money")
		
		l = label(self, "XP: ")
		l.width = 50
		self.moneydrawer.pack(l)
		
		xp = entry(self, 100, numbers=True)
		self.moneydrawer.pack(xp, "right")
		self.link(xp, "xp", 0)
		
		l = label(self, "Gold: ")
		l.width = 50
		self.moneydrawer.pack(l)
		
		gold = entry(self, 100, numbers=True)
		self.moneydrawer.pack(gold, "right")
		self.link(gold, "gp", 0)
		
		l = label(self, "gp")
		self.moneydrawer.pack(l, "right")
		
		self.pack(self.moneydrawer)
		
		# Skills
		
		self.skillsdrawer = drawer(self, "Skills")
		
		self.skillsdrawer.pack(label(self, "Skills", fontsize=largefontsize))
				
		l = label(self, "skill name")
		l.width = 150
		self.skillsdrawer.pack(l)
		
		l = label(self, "abil")
		l.width = 30
		self.skillsdrawer.pack(l, "right")
		
		l = label(self, "modif")
		l.width = abilitywidth
		self.skillsdrawer.pack(l, "right")
		
		l = label(self, "ranks")
		l.width = abilitywidth
		self.skillsdrawer.pack(l, "right")
		
		l = label(self, "abil")
		l.width = abilitywidth
		self.skillsdrawer.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.skillsdrawer.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.skillsdrawer.pack(l, "right")
		
		for skill, ability in skills:
			l = label(self, skill)
			l.width = 150
			self.skillsdrawer.pack(l)
			
			l = label(self, ability)
			l.width = 30
			self.skillsdrawer.pack(l, "right")
			
			total = entry(self, numboxwidth, numbers=True)
			self.skillsdrawer.pack(total, "right")
			self.link(total, skill + " total", 0)
			
			self.skillsdrawer.pack(label(self, "="), "right")
			
			ranks = entry(self, numboxwidth, numbers=True)
			self.skillsdrawer.pack(ranks, "right")
			self.link(ranks, skill + " ranks", 0)
			
			self.skillsdrawer.pack(label(self, "+"), "right")
			
			abil = entry(self, numboxwidth, numbers=True)
			self.skillsdrawer.pack(abil, "right")
			self.link(abil, skill + " ability", 0)
			
			self.skillsdrawer.pack(label(self, "+"), "right")
			
			miscplus = entry(self, numboxwidth, numbers=True)
			self.skillsdrawer.pack(miscplus, "right")
			self.link(miscplus, skill + " misc plus", 0)
			
			self.skillsdrawer.pack(label(self, "-"), "right")

			miscminus = entry(self, numboxwidth, numbers=True)
			self.skillsdrawer.pack(miscminus, "right")
			self.link(miscminus, skill + " misc minus", 0)
			
			self.function(self.same, [self.abilitymodifiers[ability]], abil)
			self.function(self.skill, [ranks, abil, miscplus, miscminus], total)
		
		self.pack(self.skillsdrawer)
		
		# Special Abilities
		
		self.specialdrawer = drawer(self, "Special Abilities")
		
		features = listbox(self, "racial traits/class features", [])
		self.specialdrawer.pack(features)
		self.link(features, "racial traits class features", [])
		
		self.pack(self.specialdrawer)
		
		# Possessions
		
		self.possessionsdrawer = drawer(self, "Possessions")

		onperson = listbox(self, "Possessions on person", [])
		self.possessionsdrawer.pack(onperson)
		self.link(onperson, "possessions on person", [])
		
		offperson = listbox(self, "Possessions off person", [])
		self.possessionsdrawer.pack(offperson)
		self.link(offperson, "possessions off person", [])
				
		self.pack(self.possessionsdrawer)
		
		# Magic
		
		self.magicdrawer = drawer(self, "Magic")
		
		self.magicdrawer.pack(label(self, "In order to use magic you must first unlock the achievement"))
		
		self.pack(self.magicdrawer)
		
	def same(self, source):
		return int(source)
	
	def savescore(self, base, ability, magic, miscplus, miscminus):
		return int(base) + int(ability) + int(magic) + int(miscplus) - int(miscminus)

	def abilityscore(self, base, race, enhancement, miscplus, miscminus):
		return int(base) + int(race) + int(enhancement) + int(miscplus) - int(miscminus)
	
	def abilitymodifier(self, total):
		return int((int(total) - 10) / 2)
	
	def add(self, thing1, thing2):
		return int(thing1) + int(thing2)
	
	def armorclass(self, armor, shield, dex, size, natural, deflection, miscplus, miscminus):
		return 10 + int(armor) + int(shield) + int(dex) + int(size) + int(natural) + int(deflection) + int(miscplus) - int(miscminus)

	def flatarmorclass(self, armor, shield, dex, size, natural, deflection, miscplus, miscminus):
		return 10 + int(armor) + int(shield) + int(size) + int(natural) + int(deflection) + int(miscplus) - int(miscminus)

	def toucharmorclass(self, armor, shield, dex, size, natural, deflection, miscplus, miscminus):
		return 10 +int(dex) + int(size) + int(natural) + int(deflection) + int(miscplus) - int(miscminus)
	
	def skill(self, ranks, abil, miscplus, miscminus):
		return int(ranks) + int(abil) + int(miscplus) - int(miscminus)
	
editors = {"npc":npceditor}
