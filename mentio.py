from helpers import *
from re import compile as reg_compile
from traceback import format_exc as print_traceback


mentions   = open_json_file("mentio", {})
max_amount = 3
arrow      = colorify(u"&r&7\u2192&r")
colors_reg = reg_compile(u"\u00A7[\\da-fk-or]")


@hook.event("player.AsyncPlayerChatEvent", "high")
def onChat(event):
  if not event.isCancelled():
    sender     = event.getPlayer()
    words      = event.getMessage().split(" ")
    recipients = event.getRecipients()

    for recipient in list(recipients):
      listeners   = mentions[str(recipient.getUniqueId())]
      rec_words = words[:] # copy
      for i in range(len(rec_words)):
        word = rec_words[i]
        isMentioned = False

        if recipient.getName().lower() in word.lower(): # is the player's full ign in the list
          isMentioned = True

        if word.lower() in [i.lower() for i in listeners]: # is the word in the listeners list
          isMentioned = True

        if isMentioned:
          # join all color codes used upto this word
          colors = "".join(colors_reg.findall("".join(words[:i+1])))
          # highlight word containing mention, then apply all previous color codes
          rec_words[i] = colorify("&r&a&n") + stripcolors(word) + colorify("&r") + colors

      # player was mentioned
      if rec_words != words:
        try:
          recipients.remove(recipient) # don't send original message
        except:
          # list might not be mutable, ignoring. Receiver will get the message twice
          pass
        message = " ".join([sender.getDisplayName(), arrow] + rec_words)
        msg(recipient, message, usecolor = False)
        recipient.playSound(recipient.getLocation(), "liquid.lavapop", 1, 2)


@hook.command("listen")
def onListenCommand(sender, args):
  currWords = []
  if str(sender.getUniqueId()) in mentions.keys():
    currWords = mentions[str(sender.getUniqueId())]

  # /listen add <word>
  if len(args) == 2 and args[0].lower() == "add":

    if len(currWords) >= max_amount:
      msg(sender, "&cYou are already listening for %s words! Try &6/listen del <word>" % max_amount)
      return True
    if len(args[1].lower()) > 16:
      msg(sender, "&cThis word is longer than 16 characters. Pick a shorter one!")
    if args[1].lower() in currWords:
      msg(sender, "&cYou are already listening for this word! Try &6/listen list")
      return True
    if args[1].lower() is sender.getName():
      msg(sender, "&cYou are always listening for your full ingame name by default")
    currWords.append(args[1].lower())
    mentions[str(sender.getUniqueId())] = currWords
    msg(sender, "&aYou are now listening for '&2%s'!" % args[1].lower())
    saveMentions()
    return True
  # /listen del <word>
  elif len(args) == 2 and args[0].lower() == "del":
    if len(currWords) <= 0:
      msg(sender, "&cYou are currently listening for no words! Try &6/listen add <word>")
      return True
    success = False
    for word in currWords[:]:
      if word.lower() == args[1].lower():
        currWords.remove(word.lower())
        mentions[str(sender.getUniqueId())] = currWords
        success = True
    if success == True:
      saveMentions()
      msg(sender, "&eYou are no longer listening for '&2%s&e'!" % args[1].lower())
    else:
      msg(sender, "&cWe can't remove something that doesn't exist! Try &6/listen list")
    return True

  # /listen list
  elif len(args) == 1 and args[0].lower() == "list":
    msg(sender, "&6Words you're listening for:")
    for word in currWords:
      msg(sender, "&c- &3"+word)
  else:
    msg(sender, "&eNobody calls you %s &efor some particular reason? Too long? Add some aliases!\n\n" % sender.getDisplayName())
    msg(sender, "&6/listen add <word>")
    msg(sender, "&6/listen del <word>")
    msg(sender, "&6/listen list")


def saveMentions():
  save_json_file("mentio", mentions)