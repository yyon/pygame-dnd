from gui import * #@UnusedWildImport
import functools
import data

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

		self.pack(label(self, "Details", fontsize=largefontsize))
		
		l = label(self, "full name: ")
		l.width = 50
		self.pack(l)
		
		name = entry(self, 100)
		self.pack(name, "right")
		self.link(name, "fullname", entity)
		
		l = label(self, "class: ")
		l.width = 50
		self.pack(l)
		
		classentry = entry(self, 100)
		self.pack(classentry, "right")
		self.link(classentry, "class", "")
		
		l = label(self, "level: ")
		l.width = 50
		self.pack(l)
		
		lvl = entry(self, 50, numbers=True)
		self.pack(lvl, "right")
		self.link(lvl, "level", "0")
		
		l = label(self, "race: ")
		l.width = 50
		self.pack(l)
		
		race = entry(self, 100)
		self.pack(race, "right")
		self.link(race, "race", "")
		
		l = label(self, "alignment: ")
		l.width = 50
		self.pack(l)
		
		alignment = entry(self, 100)
		self.pack(alignment, "right")
		self.link(alignment, "alignment", "")

		self.pack(label(self, "Hit Points", fontsize=largefontsize))
		
		l = label(self, "total hp: ")
		l.width = 50
		self.pack(l)
		
		hp = entry(self, numboxwidth, numbers=True)
		self.pack(hp, "right")
		self.link(hp, "hit points", "0")
		
		self.pack(label(self, "Ability Scores", fontsize=largefontsize))
		
		l = label(self, "")
		l.width = 20
		self.pack(l)
		
		l = label(self, "score")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "base")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "race")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "magic")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "modifier")
		l.width = abilitywidth
		self.pack(l, "right")
		
		saveabilities = {}
		self.abilitymodifiers = {}
		
		for ability in ["str","dex","con","int","wis","cha"]:
			abilitylabel = label(self, ability)
			abilitylabel.width = 20
			self.pack(abilitylabel)
			
			total = entry(self, numboxwidth, numbers=True)
			self.pack(total, "right")
			self.link(total, ability+" total", 10)
			
			self.pack(label(self, "="), "right")
			
			base = entry(self, numboxwidth, numbers=True)
			self.pack(base, "right")
			self.link(base, ability+" base", 10)
			
			self.pack(label(self, "+"), "right")
			
			race = entry(self, numboxwidth, numbers=True)
			self.pack(race, "right")
			self.link(race, ability+" race", 0)
			
			self.pack(label(self, "+"), "right")
			
			enhancement = entry(self, numboxwidth, numbers=True)
			self.pack(enhancement, "right")
			self.link(enhancement, ability+" enhancement", 0)
			
			self.pack(label(self, "+"), "right")
			
			miscplus = entry(self, numboxwidth, numbers=True)
			self.pack(miscplus, "right")
			self.link(miscplus, ability+" misc plus", 0)
			
			self.pack(label(self, "-"), "right")
			
			miscminus = entry(self, numboxwidth, numbers=True)
			self.pack(miscminus, "right")
			self.link(miscminus, ability+" misc minus", 0)
			
			self.pack(label(self, "|"), "right")
			
			modifier = entry(self, numboxwidth, numbers=True)
			self.pack(modifier, "right")
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

		self.pack(label(self, "Combat Options", fontsize=largefontsize))
		
		l = label(self, "base attack bonus: ")
		self.pack(l)
		
		bab = entry(self, numboxwidth, numbers=True)
		self.pack(bab, "right")
		self.link(bab, "base attack bonus", "0")

		l = label(self, "weapon")
		l.width = 100
		self.pack(l)
		
		l = label(self, "attack")
		l.width = 40
		self.pack(l, "right")
		
		l = label(self, "damage")
		l.width = 50
		self.pack(l, "right")
		
		l = label(self, "crit")
		l.width = 50
		self.pack(l, "right")
				
		for weapon in range(4):
			weaponname = entry(self, 100)
			self.pack(weaponname)
			self.link(weaponname, "weapon "+str(weapon), "")
			
			attack = entry(self, 40, numbers=True)
			self.pack(attack, "right")
			self.link(attack, "weapon attack "+str(weapon), 0)
			
			dmg = entry(self, 50)
			self.pack(dmg, "right")
			self.link(dmg, "weapon damage "+str(weapon), "")
			
			crit = entry(self, 50)
			self.pack(crit, "right")
			self.link(crit, "weapon crit "+str(weapon), "")

		self.pack(label(self, "Speed", fontsize=largefontsize))
		
		l = label(self, "speed: ")
		l.width = 50
		self.pack(l)
		
		speed = entry(self, 50, numbers=True)
		self.pack(speed, "right")
		self.link(speed, "speed", "0")
		
		l = label(self, "initiative: ")
		l.width = 50
		self.pack(l)
		
		init = entry(self, 50, numbers=True)
		self.pack(init, "right")
		self.link(init, "initiative", "0")
		
		self.pack(label(self, "Grapple", fontsize=largefontsize))
		
		l = label(self, "grapple: ")
		l.width = 50
		self.pack(l)
		
		grapple = entry(self, 50, numbers=True)
		self.pack(grapple, "right")
		self.link(grapple, "grapple", "0")
		
		self.pack(label(self, "Saving Throws", fontsize=largefontsize))
		
		l = label(self, "")
		l.width = 20
		self.pack(l)
		
		l = label(self, "total")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "base")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "ability")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "magic")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.pack(l, "right")

		for save in ["fort", "ref", "will"]:
			abilitylabel = label(self, save)
			abilitylabel.width = 20
			self.pack(abilitylabel)
			
			total = entry(self, numboxwidth, numbers=True)
			self.pack(total, "right")
			self.link(total, save+" total", 0)
			
			self.pack(label(self, "="), "right")
			
			base = entry(self, numboxwidth, numbers=True)
			self.pack(base, "right")
			self.link(base, save+" base", 0)
			
			self.pack(label(self, "+"), "right")
			
			ability = entry(self, numboxwidth, numbers=True)
			self.pack(ability, "right")
			self.link(ability, save+" ability", 0)
					
			self.pack(label(self, "+"), "right")
			
			magic = entry(self, numboxwidth, numbers=True)
			self.pack(magic, "right")
			self.link(magic, save+" magic", 0)
			
			self.pack(label(self, "+"), "right")
			
			miscplus = entry(self, numboxwidth, numbers=True)
			self.pack(miscplus, "right")
			self.link(miscplus, save+" misc plus", 0)
					
			self.pack(label(self, "-"), "right")
			
			miscminus = entry(self, numboxwidth, numbers=True)
			self.pack(miscminus, "right")
			self.link(miscminus, save+" misc minus", 0)
			
			self.function(self.savescore, [base, ability, magic, miscplus, miscminus], total)
			self.function(self.same, [saveabilities[save]], ability)

		self.pack(label(self, "Armor", fontsize=largefontsize))
		
		l = label(self, "total")
		l.width = abilitywidth
		self.pack(l)
		
		l = label(self, "")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "armor")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "shield")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "dex")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "size")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "natrl")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "deflect")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.pack(l, "right")
		
		total = entry(self, numboxwidth, numbers=True)
		self.pack(total)
		self.link(total, "AC total", 10)
		
		self.pack(label(self, "="), "right")
		
		l = label(self, "10")
		l.width = numboxwidth
		self.pack(l, "right")

		self.pack(label(self, "+"), "right")
		
		armor = entry(self, numboxwidth, numbers=True)
		self.pack(armor, "right")
		self.link(armor, "AC armor", 0)
		
		self.pack(label(self, "+"), "right")
				
		shield = entry(self, numboxwidth, numbers=True)
		self.pack(shield, "right")
		self.link(shield, "AC shield", 0)
		
		self.pack(label(self, "+"), "right")
				
		dex = entry(self, numboxwidth, numbers=True)
		self.pack(dex, "right")
		self.link(dex, "AC dex", 0)
		self.function(self.same, [self.abilitymodifiers["dex"]], dex)
		
		self.pack(label(self, "+"), "right")
				
		size = entry(self, numboxwidth, numbers=True)
		self.pack(size, "right")
		self.link(size, "AC size", 0)
		
		self.pack(label(self, "+"), "right")
				
		natural = entry(self, numboxwidth, numbers=True)
		self.pack(natural, "right")
		self.link(natural, "AC natural", 0)
		
		self.pack(label(self, "+"), "right")
				
		deflection = entry(self, numboxwidth, numbers=True)
		self.pack(deflection, "right")
		self.link(deflection, "AC deflection", 0)
		
		self.pack(label(self, "+"), "right")
		
		miscplus = entry(self, numboxwidth, numbers=True)
		self.pack(miscplus, "right")
		self.link(miscplus, "AC misc plus", 0)
		
		self.pack(label(self, "-"), "right")
				
		miscminus = entry(self, numboxwidth, numbers=True)
		self.pack(miscminus, "right")
		self.link(miscminus, "AC misc minus", 0)
		
		self.function(self.armorclass, [armor, shield, dex, size, natural, deflection, miscplus, miscminus], total)

		l = label(self, "touch: ")
		l.width = 50
		self.pack(l)
		
		touch = entry(self, 100, numbers=True)
		self.pack(touch, "right")
		self.link(touch, "AC touch", 10)
		
		self.function(self.toucharmorclass, [armor, shield, dex, size, natural, deflection, miscplus, miscminus], touch)
		
		l = label(self, "flat-footed: ")
		l.width = 50
		self.pack(l)
		
		flat = entry(self, 100, numbers=True)
		self.pack(flat, "right")
		self.link(flat, "AC flatfooted", 10)
		
		self.function(self.flatarmorclass, [armor, shield, dex, size, natural, deflection, miscplus, miscminus], flat)
		
		l = label(self, "")
		l.width = 50
		self.pack(l)
				
		l = label(self, "type")
		l.width = 100
		self.pack(l, "right")
				
		l = label(self, "max dex")
		l.width = 50
		self.pack(l, "right")
				
		l = label(self, "armor check")
		l.width = 70
		self.pack(l, "right")
				
		l = label(self, "weight")
		l.width = 50
		self.pack(l, "right")
		
		for armortype in ["armor", "shield"]:
			l = label(self, armortype)
			l.width = 50
			self.pack(l)
			
			nametype = entry(self, 100)
			self.pack(nametype, "right")
			self.link(nametype, armortype + " type", "")
			
			maxdex = entry(self, 50, numbers=True)
			self.pack(maxdex, "right")
			self.link(maxdex, armortype + " max dex", 0)
			
			acpenalty = entry(self, 70, numbers=True)
			self.pack(acpenalty, "right")
			self.link(acpenalty, armortype + " armor check penalty", 0)
			
			weight = entry(self, 50, numbers=True)
			self.pack(weight, "right")
			self.link(weight, armortype + " weight", 0)
		
		self.pack(label(self, "XP / Money", fontsize=largefontsize))
		
		l = label(self, "XP: ")
		l.width = 50
		self.pack(l)
		
		xp = entry(self, 100, numbers=True)
		self.pack(xp, "right")
		self.link(xp, "xp", 0)
		
		l = label(self, "Gold: ")
		l.width = 50
		self.pack(l)
		
		gold = entry(self, 100, numbers=True)
		self.pack(gold, "right")
		self.link(gold, "gp", 0)
		
		l = label(self, "gp")
		self.pack(l, "right")
		
		self.pack(label(self, "Skills", fontsize=largefontsize))
				
		l = label(self, "skill name")
		l.width = 150
		self.pack(l)
		
		l = label(self, "abil")
		l.width = 30
		self.pack(l, "right")
		
		l = label(self, "modif")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "ranks")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "abil")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.pack(l, "right")
		
		l = label(self, "misc")
		l.width = abilitywidth
		self.pack(l, "right")
		
		for skill, ability in skills:
			l = label(self, skill)
			l.width = 150
			self.pack(l)
			
			l = label(self, ability)
			l.width = 30
			self.pack(l, "right")
			
			total = entry(self, numboxwidth, numbers=True)
			self.pack(total, "right")
			self.link(total, skill + " total", 0)
			
			self.pack(label(self, "="), "right")
			
			ranks = entry(self, numboxwidth, numbers=True)
			self.pack(ranks, "right")
			self.link(ranks, skill + " ranks", 0)
			
			self.pack(label(self, "+"), "right")
			
			abil = entry(self, numboxwidth, numbers=True)
			self.pack(abil, "right")
			self.link(abil, skill + " ability", 0)
			
			self.pack(label(self, "+"), "right")
			
			miscplus = entry(self, numboxwidth, numbers=True)
			self.pack(miscplus, "right")
			self.link(miscplus, skill + " misc plus", 0)
			
			self.pack(label(self, "-"), "right")

			miscminus = entry(self, numboxwidth, numbers=True)
			self.pack(miscminus, "right")
			self.link(miscminus, skill + " misc minus", 0)
			
			self.function(self.same, [self.abilitymodifiers[ability]], abil)
			self.function(self.skill, [ranks, abil, miscplus, miscminus], total)

		self.pack(label(self, "Special Abilities", fontsize=largefontsize))
		
		features = listbox(self, "racial traits/class features", [])
		self.pack(features)
		self.link(features, "racial traits class features", [])
		
		self.pack(label(self, "Possessions", fontsize=largefontsize))
		
		self.pack(label(self, "Magic", fontsize=largefontsize))
		
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
	
class detailsdrawer(drawer):
	def __init__(self, window):
		drawer.__init__(self, window, "Details")
		self.editor = window
		
	def packitems(self):
		pass

editors = {"npc":npceditor}
