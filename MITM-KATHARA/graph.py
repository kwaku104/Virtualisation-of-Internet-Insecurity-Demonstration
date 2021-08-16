import algorithmx
import subprocess

# Create a new HTTP server
server = algorithmx.http_server(port=5050)
# Create a CanvasSelection interface
canvas = server.canvas()


def getJsonTopology():
    deviceList = []
    devicePayLoad = []

    with open('/Users/kwakuappiah-adu/Documents/lboro/Final-Project/Virtualisation-of-Internet-Insecurity-Demonstration/MITM-KATHARA/lab.conf', 'r') as f:
        for line in f:
            if '[' not in line:
                continue
            if line[:line.index('[')] not in deviceList:
                deviceDict = {}
                if line[:line.index('[')] == 'server':
                    endofLine = -1
                else:
                    endofLine = -2
                deviceList.append(line[:line.index('[')])
                deviceDict['device_name'] = line[:line.index('[')]
                deviceDict['interfaces'] = [
                    (f"eth{line[line.index('[')+1:line.index(']')]}", line[line.index('=')+2:endofLine])]
                devicePayLoad.append(deviceDict)
            else:
                deviceDict['interfaces'].append(
                    (f"eth{line[line.index('[')+1:line.index(']')]}", line[line.index('=')+2:-2]))
    # j = 0
    intList = []
    for i in range(len(devicePayLoad)):
        devicePayLoad[i]['interfaces'] = dict(
            devicePayLoad[i]['interfaces'])

        ipProcess = subprocess.Popen(
            ["kathara", "exec", deviceList[i], "--", "hostname", "-I"], stdout=subprocess.PIPE)
        ipProcess = ipProcess.stdout.readline()
        ipProcess = ipProcess.rstrip().decode("utf-8")
        ipProcess = ipProcess.split(' ')
        for j in range(len(ipProcess)):
            devicePayLoad[i]['interfaces'][f'eth{j}'] = {
                'collision_domain': devicePayLoad[i]['interfaces'][f'eth{j}'],
                'ip_address': ipProcess[j]
            }
            # print("1 Completed")
    return devicePayLoad


topolopgy = getJsonTopology()
# print(topolopgy)
# breakpoint()
deviceList = []
for config in topolopgy:
    deviceList.append(config['device_name'])
    # print(config['interfaces'].values())
# print(deviceList)
edgeList = []
for interface in range(len(topolopgy)):
    interfaceList = list(topolopgy[interface]
                         ['interfaces'].values())
    interfaceList = [domain['collision_domain'] for domain in interfaceList]
    # print(interfaceList)
    # breakpoint()
    setInterfaceList = set(interfaceList)
    for matchingInterface in topolopgy[1:]:
        matchingInterfaceList = list(
            matchingInterface['interfaces'].values())
        # print(matchingInterfaceList)
        matchingInterfaceList = [domain['collision_domain']
                                 for domain in matchingInterfaceList]
        if interfaceList == matchingInterfaceList:
            continue
        setMatchingInterfaceList = set(matchingInterfaceList)
        if setInterfaceList & setMatchingInterfaceList:
            edgeList.append(
                (topolopgy[interface]['device_name'], matchingInterface['device_name']))
    # print(edgeList)


def get_routePath(device):
    routePathList = []

    process = subprocess.Popen(
        ["kathara", "exec", device, "--", "vtysh", "-c show ip bgp"], stdout=subprocess.PIPE)
    while True:
        nextHopDict = {}
        line = process.stdout.readlines()
        # [20:29] * 200.6.0.0/17     199.9.9.6
        # for node in topolopgy:
        # print(line.rstrip().decode("utf-8"))
        line = [line.rstrip().decode("utf-8") for line in line]
        for lineIndex in range(len(line)):
            print(line[lineIndex])
        # breakpoint()
            if line[lineIndex][:15] == '*> 200.7.0.0   ':
                nextHop = line[lineIndex][20:40]
                nextHop = nextHop.strip()
                # nextHopDict['*> 200.7.0.0'] = nextHop
                print(f'First condition (*> 200.7.0.0   ): {nextHop}')
                pass
                # continue
                # pathList = [char for char in line.rstrip().decode("utf-8")[59:]]
                # print("Changed!!!")

            elif line[lineIndex][:15] == '*> 200.7.0.0/16':
                nextHop = line[lineIndex][20:40]
                nextHop = nextHop.strip()
                # nextHop['*> 200.7.0.0/16'] = nextHop
                print(f'Second condition (*> 200.7.0.0/16): {nextHop}')
                pass
                # continue
                # pathList = [char for char in line.rstrip().decode("utf-8")[59:]]

            elif line[lineIndex][:15] == '*  200.7.0.0/16' or line[lineIndex][:15] == '*  200.7.0.0   ':
                # line = process.stdout.readline()
                # print(line.rstrip().decode("utf-8")[:40])
                if line[lineIndex + 1][:2] == '*>':
                    nextHop = line[lineIndex + 1][20:40]
                else:
                    nextHop = line[lineIndex + 2][20:40]
                nextHop = nextHop.strip()
                # nextHop['*  200.7.0.0/16'] = nextHop
                print(
                    f'Third condition (*  200.7.0.0/16 or *  200.7.0.0): {nextHop}')
                pass
                # continue
            else:
                continue
            cursor = 0
            for node in topolopgy:
                # print(
                # f"name: {node['device_name']} || interface: {node['interfaces']}")
                # break
                for interface in range(len(node['interfaces'])):
                    # print(node['interfaces'][f'eth{interface}']['ip_address'])
                    # print(interface)
                    if node['interfaces'][f'eth{interface}']['ip_address'] == nextHop and (device, node['device_name']) not in routePathList:
                        routePathList.append((device, node['device_name']))
                    if len(routePathList) > 1:
                        del routePathList[0]
                # breakpoint()
                # else:
                #     continue
                #     print('found 1')
                # cursor += 1
        print(routePathList)
        # breakpoint()
        # pathList = ' '.join(pathList).split()
        # print(pathList)
        # j = 1
        # for i in pathList[:-2]:
        #     if i == '0':
        #         routePathList.append((device, pathDict[pathList[j]]))
        #     else:
        #         routePathList.append((pathDict[i], pathDict[pathList[j]]))
        #     j += 1
        return routePathList

# get_routePath()


def click():
    canvas.node('start').highlight().size('1x').pause(0.5)
    canvas.pause(1)
    # canvas.edges(edgeListUnique).add(directed=True)
    colours = ['blue', 'red', 'green', 'violet',
               'yellow', 'purple', 'black', 'Orange']

    col = 0
    for device in deviceList:
        if device == 'server' or device == 'dumpserver' or device == 'router2':
            continue
        print(device)
        route = get_routePath(device)
        print(f'This is the route path: {route}')
        # print(route)
        canvas.node(device).highlight().size('1.5x').pause(0.5)
        canvas.edges(route).add(directed=True)
        canvas.edges(route).traverse(colours[col])
        # map(lambda routeTup: canvas.edge(
        #     routeTup).traverse(colours[col]), route)
        canvas.node(device).onclick(print('clicked!'))
        print(f" col: {col} & lenght: {len(colours)}")
        if col < len(colours) - 1:
            col += 1


def start():
    # edgeList = []

    # Use the library normally, for example:
    # canvas.size((300, 200))
    # canvas.nodes(deviceList).add()

    # for i in range(len(deviceList)):
    #     canvas.node(deviceList[i]).add(size=20)
    #     canvas.node(deviceList[i]).label(i).add(
    #         text=f"{deviceList[i]}", color='red', size=15)

    # for edge in edgeList:
    #     canvas.edge(edge).add(directed=True)

    # deviceListDict = {deviceList.index(device): {'device': device, 'AS': f'AS-{deviceList.index(device)}'}
    #                   for device in deviceList if device == 'server'}
    deviceListDict = {}
    print(deviceList)
    for device in deviceList:
        if device == 'server':
            autonomousSystem = 'AS-2'
        elif device == 'dumpserver':
            autonomousSystem = 'AS-8'
        else:
            autonomousSystem = f'AS-{deviceList.index(device) + 1}'
        deviceListDict[device] = {
            'device': device, 'AS': f'{autonomousSystem}'}

    keys, values = deviceListDict.keys(), deviceListDict.values()

    canvas.node('start').add(
        shape='rect',
        size=(42, 20),
        pos=((3 - 2) * 35, (13 - 2) * 35),
        labels={0: {'text': 'Click to start!'}}
    )

    canvas.nodes(keys).data(values).add(
        shape='circle',
        size=35,
        labels=lambda d: {
            0: {'text': d['device']},
            'ASN': {
                'angle': 90,
                'color': 'red',
                'text': d['AS']
            }
        }
    )

    node_coords = [(-10, -2), (3, -2), (16, -2), (3, 4), (-10, 4),
                   (3, 9), (16, 9), (-10, 9), (-17, 9), (3, -7)]

    canvas.nodes(deviceList).data(node_coords).add(
        pos=lambda p: ((p[0] - 2) * 35, (p[1] - 2) * 35),
        fixed=True,
    )

    global edgeListUnique
    print(edgeList)
    edgeListSorted = [tuple(sorted(edge)) for edge in edgeList]
    edgeListUnique = list(set(edgeListSorted))
    canvas.edges(edgeListUnique).add()

    print('refreshed!')
    canvas.node('start').onclick(click)

    # canvas.node(1).highlight().size('1.5x').pause(0.5)
    # canvas.edge((1, 2)).traverse('blue')
    # canvas.edge((2, 4)).traverse('blue')
    # canvas.edge((4, 6)).traverse('blue')


# Call the function above when the client broadcasts a 'start' message
# (which will happen when the user clicks the start or restart button)
canvas.onmessage('start', start)
# Start the server, blocking all further execution on the current thread
# You can press 'CTRL-C' to exit the script
server.start()
