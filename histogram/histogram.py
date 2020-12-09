#!../pypy3.7-v7.3.2-linux64/bin/pypy3
import argparse
import simplejson as json

def toInt(x):
    try:
        return int(x)
    except TypeError:
        return 0

class StatusMachine(object):
    current_status = 'LEARN'
    last_stride = None
        
    def StatusMachine(self):
        pass

    def update(self, stride=None):
        if self.current_status == 'LEARN':
            self.current_status = 'STEADY'

        elif self.current_status == 'STEADY':
            if (self.last_stride == None) or (self.last_stride == stride):
                self.current_status = 'STEADY'
            else: 
                self.current_status = 'NON-LINEAR' 

        elif self.current_status == 'NON-LINEAR':
            pass

        self.last_stride = stride
        return self.current_status

parser = argparse.ArgumentParser(
    description='Create memory stride histogram from memory trace.'
)
parser.add_argument('-t', '--trace', dest='trace')
args = parser.parse_args()

program_name = 'astar'

def updateAccessInfo(memory_access_info, address, status_state_machine):
    stride = toInt(address) - toInt(memory_access_info['last_address'])

    memory_access_info['last_address'] = address
    memory_access_info['stride'] = stride
    memory_access_info['status'] = status_state_machine.update(stride)

    return (memory_access_info, status_state_machine)

memory_instructions_info = {}
memory_instructions_statuses = {}
with open(args.trace, 'r') as mem:
    line = mem.readline()
    while line:
        instruction_info = {
            'read': {
                'first_address': None,
                'last_address': None,
                'stride': None,
                'status': None
            },
            'read2': {
                'first_address': None,
                'stride': None,
                'last_address': None,
                'status': None
            },
            'write': {
                'first_address': None,
                'stride': None,
                'last_address': None,
                'status': None
            },
            'count': 0
        }
        status = {
            'read': StatusMachine(),
            'read2': StatusMachine(),
            'write': StatusMachine()
        }

        instruction, read_address, read2_address, write_address = line.split()
        
        if instruction in memory_instructions_info.keys():
            instruction_info = memory_instructions_info[instruction]
            status = memory_instructions_statuses[instruction]

        if read_address != '-1':
            if instruction_info['read']['first_address'] == None:
                instruction_info['read']['first_address'] = read_address
                instruction_info['read']['last_address'] = read_address
                instruction_info['read']['status'] = status['read'].update()

            else:
                instruction_info['read'], status['read'] = updateAccessInfo(
                    instruction_info['read'], read_address, status['read']
                )
              
        if read2_address != '-1':
            if instruction_info['read2']['first_address'] == None:
                instruction_info['read2']['first_address'] = read2_address
                instruction_info['read2']['last_address'] = read2_address
                instruction_info['read2']['status'] = status['read2'].update()

            else:
                instruction_info['read2'], status['read2'] = updateAccessInfo(
                    instruction_info['read2'], read2_address, status['read2']
                )

        if write_address != '-1':
            if instruction_info['write']['first_address'] == None:
                instruction_info['write']['first_address'] = write_address
                instruction_info['write']['last_address'] = write_address
                instruction_info['write']['status'] = status['write'].update()

            else:
                instruction_info['write'], status['write'] = updateAccessInfo(
                    instruction_info['write'], write_address, status['write']
                )

        instruction_info.update({'count': instruction_info['count'] + 1})
        memory_instructions_info.update({instruction: instruction_info})
        memory_instructions_statuses.update({instruction: status})

        line = mem.readline()

with open('strides_' + program_name + '.json', 'w+') as memory_info_json:
    json.dump(memory_instructions_info, memory_info_json)
