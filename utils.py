import ipaddress
def is_IpMaskValid(ip : str = "192.168.0.1",
                   mask : str = "255.255.255.0"):
  try:
      ip = ipaddress.IPv4Network(ip + "/" + mask, False)
      return True
  except ValueError:
      return False

def consructLog(file: str):
  file_сontent = ""
  with open(file, "r") as f:
    for line in f:
      file_сontent += line
      file_сontent += "\n"
  return file_сontent

def networksIpCounter(ip, mask, comps):
  comps = list(map(int,comps.split()))

  add_ip = [3, 4, 5, 3, 3]
  network = ipaddress.IPv4Network(ip + "/" + mask, False)
  networks = {}
  for i in range(0, len(comps)): 
    index_max = comps.index(max(comps))
    n = (comps[index_max] + add_ip[index_max] - 1).bit_length() 
    subnets = list(network.subnets(new_prefix=32-n))
    networks[index_max] = subnets[0].network_address, subnets[0].netmask
    comps[index_max] = -1
    network = ipaddress.IPv4Network(str(subnets[0].broadcast_address + 1) + "/" +     str(subnets[0].netmask), False)

  return networks
  for network in sorted(networks.items()):
    print(network[0]+1,network[1][0].exploded, network[1][1].exploded)
    ans.append([network[1][0].exploded, network[1][1].exploded])

def statCollector():
  correct_answers = 0
  incorrect_answers = -1
  answers = -1
  uniq = set() 
  with open("storage.txt", "r") as file:
    for line in file.read().split("\n"):
      answers +=1
      if line.find("True", line.rfind("Correct"), line.rfind("Correct") + 17) > 0: 
        correct_answers+=1
      else: 
        incorrect_answers+=1
      uniq.add(line[ : line.find("Username")])
  return [correct_answers, incorrect_answers, answers, len(uniq)-1]