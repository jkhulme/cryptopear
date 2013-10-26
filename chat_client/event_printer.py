from termcolor import colored

def handle_event_json(parsed):
  if parsed['type'] == 'quitjoin':
    name = parsed['quitjoin']['name']
    if parsed['quitjoin']['event'] == 'join':
      return colored(''.join([parsed['time'],' -> ',name,' has joined the channel.\n']), 'yellow')
    else:
      return colored(''.join([parsed['time'],' <- ',name,' has left the channel.\n']), 'red')
  elif parsed['type'] == 'message':
    sender = parsed['message']['sender']
    return colored(''.join(['<',sender,'> ']),'green') + parsed['message']['body']
  elif parsed['type'] == 'event':
    return colored(''.join([parsed['event']['message'],'\n']),'cyan')

