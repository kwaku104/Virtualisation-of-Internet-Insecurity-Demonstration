import algorithmx
import subprocess
import os
import sys
# Create a new HTTP server
server = algorithmx.http_server(port=5050)
# Create a CanvasSelection interface
canvas = server.canvas()


def getJsonTopology():
    deviceList = []
    devicePayLoad = []

    with open(os.path.join(sys.path[0], 'lab.conf'), 'r') as f:
        for line in f:
            if '[' not in line:
                continue
            if line[:line.index('[')] not in deviceList:
                deviceDict = {}
                if line[:line.index('[')] == 'dumpserver9':
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


def getEdgeList():
    global topolopgy
    global deviceList
    topolopgy = getJsonTopology()
    print(topolopgy)
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
        interfaceList = [domain['collision_domain']
                         for domain in interfaceList]
        # print(interfaceList)
        # breakpoint()
        setInterfaceList = set(interfaceList)
        for matchingInterface in topolopgy:
            matchingInterfaceList = list(
                matchingInterface['interfaces'].values())
            # print(matchingInterfaceList)
            matchingInterfaceList = [domain['collision_domain']
                                     for domain in matchingInterfaceList]
            if interfaceList == matchingInterfaceList:
                continue
            setMatchingInterfaceList = set(matchingInterfaceList)
            print(
                f"setInterfaceList: {setInterfaceList} || setMatchingInterfaceList: {setMatchingInterfaceList}")
            if setInterfaceList & setMatchingInterfaceList:
                edgeList.append(
                    (topolopgy[interface]['device_name'], matchingInterface['device_name']))
    return edgeList


def get_routePath(device):
    routePathList = []

    process = subprocess.Popen(
        ["kathara", "exec", device, "--", "vtysh", "-c show ip bgp"], stdout=subprocess.PIPE)
    while True:
        nextHopDict = {}
        line = process.stdout.readlines()
        line = [line.rstrip().decode("utf-8") for line in line]
        for lineIndex in range(len(line)):
            print(line[lineIndex])
            if line[lineIndex][:15] == '*> 200.7.0.0   ':
                nextHop = line[lineIndex][20:40]
                nextHop = nextHop.strip()
                print(f'First condition (*> 200.7.0.0   ): {nextHop}')
                pass

            elif line[lineIndex][:15] == '*> 200.7.0.0/16':
                nextHop = line[lineIndex][20:40]
                nextHop = nextHop.strip()
                print(f'Second condition (*> 200.7.0.0/16): {nextHop}')
                pass

            elif line[lineIndex][:15] == '*  200.7.0.0/16' or line[lineIndex][:15] == '*  200.7.0.0   ':
                if line[lineIndex + 1][:2] == '*>':
                    nextHop = line[lineIndex + 1][20:40]
                else:
                    nextHop = line[lineIndex + 2][20:40]
                nextHop = nextHop.strip()
                print(
                    f'Third condition (*  200.7.0.0/16 or *  200.7.0.0): {nextHop}')
                pass
            else:
                continue
            cursor = 0
            for node in topolopgy:
                for interface in range(len(node['interfaces'])):
                    if node['interfaces'][f'eth{interface}']['ip_address'] == nextHop and (device, node['device_name']) not in routePathList:
                        routePathList.append((device, node['device_name']))
                    if len(routePathList) > 1:
                        del routePathList[0]
        print(routePathList)
        return routePathList


def animate_text(label, text):
    label \
        .visible(False) \
        .pause(0.5) \
        .text(text) \
        .visible(True) \
        .pause(0.5)


def startLab():
    canvas.node('startLab').highlight().size('1x').pause(0.5)
    startLabProcess = subprocess.Popen(
        ["kathara", "lrestart", "-o", "'image=kathara/custom-kathara-image'"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    startLabProcess = startLabProcess.stdout.readlines()
    startLabProcess = [startLabProcess.rstrip().decode("utf-8")
                       for startLabProcess in startLabProcess]
    title_label = canvas.label('title')
    title_label.add().pos((0, '0.85cy')).text('')
    for output in startLabProcess:
        animate_text(title_label, output)
        canvas.pause(0.5)
        print(output)
    animate_text(
        title_label, 'Gathering device information to plot topology ...')

    global edgeList
    edgeList = getEdgeList()
    deviceListDict = {}
    print(deviceList)
    for device in deviceList:
        if device == 'server' or device == 'router2':
            autonomousSystem = 'AS-2 VICTIM'
        elif device == 'dumpserver' or device == 'router8':
            autonomousSystem = 'AS-8 ATTACKER'
        else:
            autonomousSystem = f'AS-{device[-1]}'
        deviceListDict[device] = {
            'device': device, 'AS': f'{autonomousSystem}'}

    keys, values = deviceListDict.keys(), deviceListDict.values()

    canvas.nodes(keys).data(values).add(
        shape=lambda d: 'circle' if 'router' in d['device'] else 'rect',
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
    canvas.node('router2').color('green')
    canvas.node('router8').color('red')

    node_coords = [(-10, -2), (3, -2), (16, -2), (3, 4), (-10, 4),
                   (3, 9), (16, 9), (-10, 9), (-4, 9), (-17, 9), (3, -7), (-10, -7), (16, -7), (8, 4), (-17, 4), (3, 12), (20, 9), (-4, 4)]

    canvas.nodes(deviceList).data(node_coords).add(
        pos=lambda p: ((p[0] - 2) * 35, (p[1] - 2) * 35),
        fixed=True,
    )

    global edgeListUnique
    print(edgeList)
    edgeListSorted = [tuple(sorted(edge)) for edge in edgeList]
    edgeListUnique = list(set(edgeListSorted))
    canvas.edges(edgeListUnique).add()
    animate_text(
        title_label, 'Topology Plotted Successfully.')
    return startLabProcess


def applyFilters():
    canvas.node('applyFilters').highlight().size('1x').pause(0.5)
    dumpserverList = [
        dumpserver for dumpserver in deviceList if 'server' in dumpserver]
    for dumpserver in dumpserverList:
        if dumpserver == 'dumpserver' or dumpserver == 'server':
            continue
        print(dumpserver)
        routeFilterProcess = subprocess.Popen(
            ["kathara", "exec", dumpserver, "--", "python3", "routeFilterScript.py"], stdout=subprocess.PIPE)
        routeFilterProcess = routeFilterProcess.stdout.readlines()
        routeFilterProcess = [routeFilterProcess.rstrip().decode("utf-8")
                              for routeFilterProcess in routeFilterProcess]
        title_label = canvas.label('title')
        title_label.add().pos((0, '0.85cy')).text('')
        animate_text(title_label, 'Applying route filters to routers ...')
        for output in routeFilterProcess:
            print(output)
    for _ in range(2):
        click()
    animate_text(title_label, 'Route Filters Launched Successfully')


def launchAttack():
    canvas.node('launchAttack').highlight().size('1x').pause(0.5)
    attackProcess = subprocess.Popen(
        ["kathara", "exec", "dumpserver", "--", "python3", "launchAttack.py"], stdout=subprocess.PIPE)
    attackProcess = attackProcess.stdout.readlines()
    attackProcess = [attackProcess.rstrip().decode("utf-8")
                     for attackProcess in attackProcess]
    title_label = canvas.label('title')
    title_label.add().pos((0, '0.85cy')).text('')
    animate_text(title_label, 'Launching attack ...')
    for output in attackProcess:
        print(output)
    animate_text(title_label, 'Attack Successfully Launched')
    for _ in range(6):
        animate_text(title_label, 'Route Changes Detected ...')
        click()
    # canvas.pause(0.5)
    return attackProcess


def stopLab():
    canvas.node('stopLab').highlight().size('1x').pause(0.5)
    stopLabProcess = subprocess.Popen(
        ["kathara", "lclean"], stdout=subprocess.PIPE)
    stopLabProcess = stopLabProcess.stdout.readlines()
    stopLabProcess = [stopLabProcess.rstrip().decode("utf-8")
                      for stopLabProcess in stopLabProcess]
    title_label = canvas.label('title')
    title_label.add().pos((0, '0.85cy')).text('')
    for output in stopLabProcess:
        animate_text(title_label, output)
        # canvas.pause(0.5)
        print(output)
    animate_text(title_label, 'Lab stopped successfully')
    return stopLabProcess


def click():
    canvas.node('start').highlight().size('1x').pause(0.5)
    # edgeList = getEdgeList()
    canvas.pause(1)
    canvas.edges(edgeList).remove()
    canvas.edges(edgeListUnique).remove()
    print(f'Edge List is: {edgeList}')
    print(f'Edge List Unique is: {edgeListUnique}')
    canvas.edges(edgeListUnique).add()
    # canvas.edges(edgeListUnique).add(directed=True)
    colours = ['blue', 'red', 'green', 'violet',
               'yellow', 'purple', 'black', 'Orange']

    col = 0
    for device in deviceList:
        if 'server' in device or device == 'router2':
            continue
        print(device)
        route = get_routePath(device)
        # canvas.edges(route).remove()
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
    canvas.node('start').add(
        shape='rect',
        size=(53, 20),
        pos=((3 - 2) * 35, (15 - 2) * 35),
        color='blue',
        fixed=True,
        draggable=False,
        labels={0: {'text': 'Display Route Path'}}
    )

    canvas.node('startLab').add(
        shape='rect',
        size=(53, 20),
        pos=((-5 - 2) * 35, (15 - 2) * 35),
        color='green',
        fixed=True,
        draggable=False,
        labels={0: {'text': 'Start Lab'}}
    )

    canvas.node('launchAttack').add(
        shape='rect',
        size=(53, 20),
        pos=((7 - 2) * 35, (15 - 2) * 35),
        color='red',
        fixed=True,
        draggable=False,
        labels={0: {'text': 'Launch Attack'}}
    )

    canvas.node('stopLab').add(
        shape='rect',
        size=(53, 20),
        pos=((11 - 2) * 35, (15 - 2) * 35),
        fixed=True,
        draggable=False,
        labels={0: {'text': 'Stop Lab'}}
    )

    canvas.node('applyFilters').add(
        shape='rect',
        size=(53, 20),
        pos=((-1 - 2) * 35, (15 - 2) * 35),
        color='yellow',
        fixed=True,
        draggable=False,
        labels={0: {'text': 'Apply Route Filters'}}
    )

    print('refreshed!')
    canvas.node('start').onclick(click)
    canvas.node('startLab').onclick(startLab)
    canvas.node('applyFilters').onclick(applyFilters)
    canvas.node('launchAttack').onclick(launchAttack)
    canvas.node('stopLab').onclick(stopLab)


# Call the function above when the client broadcasts a 'start' message
# (which will happen when the user clicks the start or restart button)
canvas.onmessage('start', start)
# Start the server, blocking all further execution on the current thread
# You can press 'CTRL-C' to exit the script
server.start()
