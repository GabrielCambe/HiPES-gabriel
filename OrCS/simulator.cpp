#include "simulator.hpp"
orcs_engine_t orcs_engine;

// =============================================================================
#include <stdlib.h>     /* malloc, free, rand */
enum status_t {
    LEARN,
    STEADY,
    NON_LINEAR
};

void display_status(status_t status) {
    switch (status) {
        case LEARN:
            printf("LEARN");
            break;
        case STEADY:
            printf("STEADY");
            break;
        case NON_LINEAR:
            printf("NON_LINEAR");
            break;
        default:
            break;
    }
}

class StatusMachine {
    public:
        unsigned int first_access = 1;
        status_t current_status = LEARN;
        uint64_t last_stride;

        StatusMachine(){}

        status_t update(uint64_t stride) {
            if (current_status == LEARN){
                current_status = STEADY;
            }
            else if (current_status == STEADY){
                if ((first_access == 1) || (last_stride == stride)){
                    current_status = STEADY;
                    first_access = 0;
                }
                else {
                    current_status = NON_LINEAR; 
                } 
            }
            // else if (current_status == NON_LINEAR){
            //     ;
            // }

            last_stride = stride;
            return current_status;
        }
};

class MemoryAccessInfo {
    public:
        uint64_t first_address = 0;
        uint64_t last_address = 0;
        uint64_t stride;
        status_t status;

};

class MemoryInstructionInfo {
    public:
        uint64_t address;
        MemoryAccessInfo read;
        StatusMachine read_status;
        MemoryAccessInfo read2;
        StatusMachine read2_status;
        MemoryAccessInfo write;
        StatusMachine write_status;
        uint64_t count = 0;
};

void updateAccessInfo(MemoryAccessInfo *memory_access_info, uint64_t address, StatusMachine *status_state_machine) {
    uint64_t stride = address - memory_access_info->last_address;
    memory_access_info->last_address = address;
    memory_access_info->stride = stride;
    memory_access_info->status = status_state_machine->update(stride);
    return;
}

MemoryInstructionInfo *search_instruction_info(uint64_t address, MemoryInstructionInfo **infos, uint64_t size){
    MemoryInstructionInfo *elem = NULL;
    for (uint64_t i = 0; i < size; i++){
        if(address != infos[i]->address)
            elem = infos[i];
    }
    return elem;
}

// =============================================================================
static void display_use() {
    ORCS_PRINTF("**** OrCS - Ordinary Computer Simulator ****\n\n");
    ORCS_PRINTF("Please provide -t <trace_file_basename>");
};

// =============================================================================
static void process_argv(int argc, char **argv) {

    // Name, {no_argument, required_argument and optional_argument}, flag, value
    static struct option long_options[] = {
        {"help",        no_argument, 0, 'h'},
        {"trace",       required_argument, 0, 't'},
        {NULL,          0, NULL, 0}
    };

    // Count number of traces
    int opt;
    int option_index = 0;
    while ((opt = getopt_long_only(argc, argv, "h:t:",
                 long_options, &option_index)) != -1) {
        switch (opt) {
        case 0:
            printf ("Option %s", long_options[option_index].name);
            if (optarg)
                printf (" with arg %s", optarg);
            printf ("\n");
            break;

        case 'h':
            display_use();
            break;

        case 't':
            orcs_engine.arg_trace_file_name = optarg;
            break;
        case '?':
            break;

        default:
            ORCS_PRINTF(">> getopt returned character code 0%o ??\n", opt);
        }
    }

    if (optind < argc) {
        ORCS_PRINTF("Non-option ARGV-elements: ");
        while (optind < argc)
            ORCS_PRINTF("%s ", argv[optind++]);
        ORCS_PRINTF("\n");
    }


    if (orcs_engine.arg_trace_file_name == NULL) {
        ORCS_PRINTF("Trace file not defined.\n");
        display_use();
    }

};


// =============================================================================
int main(int argc, char **argv) {
    process_argv(argc, argv);

    /// Call all the allocate's
    orcs_engine.allocate();
    orcs_engine.trace_reader->allocate(orcs_engine.arg_trace_file_name);
    orcs_engine.processor->allocate();

    orcs_engine.simulator_alive = true;

    // =============================================================================
    uint64_t size = 0;
    uint64_t max_size = 2;
    MemoryInstructionInfo **memory_instructions_info = (MemoryInstructionInfo **) malloc(sizeof(MemoryInstructionInfo*) * max_size);
    // =============================================================================

    /// Start CLOCK for all the components
    while (orcs_engine.simulator_alive) {
        orcs_engine.processor->clock();
        orcs_engine.global_cycle++;

        // =============================================================================
        MemoryInstructionInfo *instruction_info;
        if (orcs_engine.trace_reader->current_instruction->is_read ||
            orcs_engine.trace_reader->current_instruction->is_read2 ||
            orcs_engine.trace_reader->current_instruction->is_write ) {
            
            if ((instruction_info = search_instruction_info(
                orcs_engine.trace_reader->current_instruction->opcode_address,
                memory_instructions_info,
                size
            )) == NULL){
                instruction_info = new MemoryInstructionInfo;
                instruction_info->address = orcs_engine.trace_reader->current_instruction->opcode_address;
            }

            if ( orcs_engine.trace_reader->current_instruction->is_read ) {
                if (instruction_info->count == 0) {
                    instruction_info->read.first_address = orcs_engine.trace_reader->current_instruction->read_address;
                    instruction_info->read.last_address = orcs_engine.trace_reader->current_instruction->read_address;
                    instruction_info->read.status = instruction_info->read_status.update(0);
                } else {
                    updateAccessInfo(
                        &(instruction_info->read),
                        orcs_engine.trace_reader->current_instruction->read_address,
                        &(instruction_info->read_status)
                    );
                }
            }

            if ( orcs_engine.trace_reader->current_instruction->is_read2 ) {
                if (instruction_info->count == 0) {
                    instruction_info->read2.first_address = orcs_engine.trace_reader->current_instruction->read2_address;
                    instruction_info->read2.last_address = orcs_engine.trace_reader->current_instruction->read2_address;
                    instruction_info->read2.status = instruction_info->read2_status.update(0);
                } else {
                    updateAccessInfo(
                        &(instruction_info->read2),
                        orcs_engine.trace_reader->current_instruction->read2_address,
                        &(instruction_info->write_status)
                    );
                }
            }

            if ( orcs_engine.trace_reader->current_instruction->is_write ) {
                if (instruction_info->count == 0) {
                    instruction_info->write.first_address = orcs_engine.trace_reader->current_instruction->write_address;
                    instruction_info->write.last_address = orcs_engine.trace_reader->current_instruction->write_address;
                    instruction_info->write.status = instruction_info->write_status.update(0);
                } else {
                    updateAccessInfo(
                        &(instruction_info->write),
                        orcs_engine.trace_reader->current_instruction->write_address,
                        &(instruction_info->write_status)
                    );
                }
            }

            instruction_info->count++;
            memory_instructions_info[size] = instruction_info;
            if (++size == max_size) {
                max_size *= 2;
                memory_instructions_info = (MemoryInstructionInfo **) realloc(memory_instructions_info, sizeof(MemoryInstructionInfo*) * max_size);
            }
    }

	ORCS_PRINTF("End of Simulation\n")
	orcs_engine.trace_reader->statistics();
    orcs_engine.processor->statistics();

    for (uint64_t i = 0; i < size; i++){
        memory_instructions_info[size]->address
    }

    return(EXIT_SUCCESS);
};


