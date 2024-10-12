
moderation_roles = [
  "꒰୨୧◞ 。Founders⠀.ᐟ", 
  "₊˚. ꒰ 𓂃  Owners 𓂃  ꒱ ₊˚", 
  "☕.    CO Owner    𓂃",
  "🥂 .     Ceo    𓂃", 
  "ৎ 🍻 Lead Manager𓂅", 
  "ৎ 🍸Chat Manager𓂅", 
  "ৎ 🍹Vc Manager𓂅", 
  "ৎ 🍷Senior mod 🍷𓂅", 
  "ִֶָ☾. 𓂃 Moderation 🍁"
]

def get_highest_relevant_role(member):
    # Find all roles the member has that match the moderation roles
    relevant_roles = [role for role in member.roles if role.name in moderation_roles]

    # Sort these roles according to their order in moderation_roles
    relevant_roles.sort(key=lambda role: moderation_roles.index(role.name))

    # Return the highest relevant role if found, otherwise return None
    return relevant_roles[0] if relevant_roles else None
