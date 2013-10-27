from termcolor import colored

def handle_event_json(parsed, color=False):
  if parsed['type'] == 'quitjoin':
    name = parsed['quitjoin']['name']
    if parsed['quitjoin']['event'] == 'join':
      line = ''.join([parsed['time'],' -> ',name,' has joined the channel.\n'])
      if color:
        return colored(line, 'yellow')
      else:
        return line
    else:
      line = ''.join([parsed['time'],' <- ',name,' has left the channel.\n'])
      if color:
        return colored(line, 'red')
      else:
        return line
  elif parsed['type'] == 'message':
    sender = parsed['message']['sender']
    sender = ''.join(['<',sender,'> '])
    message = parsed['message']['body']
    if color:
      return colored(sender, 'green') + message
    else:
      return ''.join([sender, message])
  elif parsed['type'] == 'event':
    return colored(''.join([parsed['event']['message'],'\n']),'cyan')

