#include "simulator.hpp"
orcs_engine_t orcs_engine;

// =============================================================================
#include <stdlib.h>     /* malloc, free, realloc */
#include <inttypes.h>

enum status_t {
    LEARN,
    STEADY,
    NON_LINEAR
};

void display_status(status_t status) {
    switch (status) {
        case LEARN:
            printf("LEARN\n");
            break;
        case STEADY:
            printf("STEADY\n");
            break;
        case NON_LINEAR:
            printf("NON_LINEAR\n");
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
        uint64_t opcode_address;
        MemoryAccessInfo read;
        StatusMachine read_status;
        MemoryAccessInfo read2;
        StatusMachine read2_status;
        MemoryAccessInfo write;
        StatusMachine write_status;
        uint64_t count = 0;
        StatusMachine status;

};

void updateAccessInfo(MemoryAccessInfo *memory_access_info, uint64_t address, StatusMachine *status_state_machine) {
    uint64_t stride = address - memory_access_info->last_address;
    memory_access_info->last_address = address;
    memory_access_info->stride = stride;
    memory_access_info->status = status_state_machine->update(stride);
    return;
}

MemoryInstructionInfo *search_instruction_info(uint64_t opcode_address, MemoryInstructionInfo *infos, uint64_t size){
    for (uint64_t i = 0; i < size; i++){
        #ifdef DEBUG
        // printf("s-%" PRIu64 " == %" PRIu64 "?\n\n", opcode_address, infos[i].opcode_address);
        #endif
        if(opcode_address == infos[i].opcode_address){
            #ifdef DEBUG
            // printf("s-%" PRIu64 "\n\n", infos[i].opcode_address);
            #endif
            return &infos[i];
        }
    }
    return NULL;
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
    #ifdef DEBUG
    uint64_t br = 0;
    #endif
    uint64_t size = 0;
    uint64_t max_size = 2;
    MemoryInstructionInfo *memory_instructions_info = (MemoryInstructionInfo *) malloc(sizeof(MemoryInstructionInfo) * max_size);
    bool is_read, is_read2, is_write, is_new_info;
    uint64_t memory_accesses = 0;
    uint64_t steady_accesses = 0;
    // =============================================================================

    /// Start CLOCK for all the components
    while (orcs_engine.simulator_alive) {
        orcs_engine.processor->clock();
        orcs_engine.global_cycle++;

        // =============================================================================
        MemoryInstructionInfo *instruction_info;
        is_read = orcs_engine.trace_reader->current_instruction->is_read;
        is_read2 = orcs_engine.trace_reader->current_instruction->is_read2;
        is_write = orcs_engine.trace_reader->current_instruction->is_write;
        if ( is_read || is_read2 || is_write ) {
            uint64_t opcode_address = orcs_engine.trace_reader->current_instruction->opcode_address;
            uint64_t read_address = orcs_engine.trace_reader->current_instruction->read_address;
            uint64_t read2_address = orcs_engine.trace_reader->current_instruction->read2_address;
            uint64_t write_address = orcs_engine.trace_reader->current_instruction->write_address;

            #ifdef DEBUG
            printf("%" PRIu64 " ", opcode_address);
            #endif

            if ((instruction_info = search_instruction_info(
                opcode_address,
                memory_instructions_info,
                size
            )) == NULL){
                instruction_info = new MemoryInstructionInfo();
                instruction_info->opcode_address = opcode_address;
                instruction_info->count = 0;
                is_new_info = true;
            } else {
                is_new_info = false;
            }

            if ( is_read ) {
                #ifdef DEBUG
                printf("%" PRIu64 " ", read_address);
                #endif
                if (instruction_info->count == 0) {
                    instruction_info->read.first_address = read_address;
                    instruction_info->read.last_address = read_address;
                    instruction_info->read.status = instruction_info->read_status.update(0);
                } else {
                    updateAccessInfo(
                        &(instruction_info->read),
                        read_address,
                        &(instruction_info->read_status)
                    );
                }
                memory_accesses++;
                if(instruction_info->read_status.current_status == STEADY)
                    steady_accesses++;
            }
            #ifdef DEBUG
            else {
                printf("-1 ");
            }
            #endif 
            
            if ( is_read2 ) {
                #ifdef DEBUG
                printf("%" PRIu64 " ", read2_address);
                #endif
                if (instruction_info->count == 0) {
                    instruction_info->read2.first_address = read2_address;
                    instruction_info->read2.last_address = read2_address;
                    instruction_info->read2.status = instruction_info->read2_status.update(0);
                } else {
                    updateAccessInfo(
                        &(instruction_info->read2),
                        read2_address,
                        &(instruction_info->read2_status)
                    );
                }
                memory_accesses++;
                if(instruction_info->read2_status.current_status == STEADY)
                    steady_accesses++;
            }
            #ifdef DEBUG
            else {
                printf("-1 ");
            }
            #endif

            if ( is_write ) {
                #ifdef DEBUG
                printf("%" PRIu64 "\n", write_address);
                #endif
                if (instruction_info->count == 0) {
                    instruction_info->write.first_address = write_address;
                    instruction_info->write.last_address = write_address;
                    instruction_info->write.status = instruction_info->write_status.update(0);
                } else {
                    updateAccessInfo(
                        &(instruction_info->write),
                        write_address,
                        &(instruction_info->write_status)
                    );
                }
                memory_accesses++;
                if(instruction_info->write_status.current_status == STEADY)
                    steady_accesses++;

            }
            #ifdef DEBUG
            else {
                printf("-1\n");
            }
            #endif

            instruction_info->count++;

            if (is_new_info) {
                memory_instructions_info[size] = (*instruction_info);

                if (++size == max_size) {
                    max_size *= 2;
                    memory_instructions_info = (MemoryInstructionInfo *) realloc(memory_instructions_info, sizeof(MemoryInstructionInfo) * max_size);
                }
            }
            #ifdef DEBUG
            br++;
            #endif
        }

        #ifdef DEBUG
        if (br >= 20)
            break;        
        #endif
    }
	ORCS_PRINTF("\nEnd of Simulation\n")
	orcs_engine.trace_reader->statistics();
    orcs_engine.processor->statistics();

    uint64_t memory_instructions = 0;
    uint64_t integrally_steady_instructions = 0;
    #ifdef DEBUG
    uint64_t non_linear_instructions = 0;
    #endif

    for (uint64_t i = 0; i < size; i++){
        #ifdef DEBUG
        printf("\nopcode_address: %lu\n", memory_instructions_info[i].opcode_address);
        #endif
        if(memory_instructions_info[i].read.status != LEARN){
            #ifdef DEBUG
            printf("read: %lu ", memory_instructions_info[i].read.stride);
            display_status(memory_instructions_info[i].read.status);
            #endif

            // Cada acesso acontece count vezes, se todas as count vezes forem STEADY, eu adiciono na contagem dos acessos steady
            memory_instructions += memory_instructions_info[i].count;
            if (memory_instructions_info[i].read.status == STEADY){
                integrally_steady_instructions += memory_instructions_info[i].count;
            }
            #ifdef DEBUG
            else { // == NON_LINEAR
                non_linear_instructions += memory_instructions_info[i].count;
            }
            #endif
        }

        if(memory_instructions_info[i].read2.status != LEARN){
            #ifdef DEBUG
            printf("read2: %lu ", memory_instructions_info[i].read2.stride);
            display_status(memory_instructions_info[i].read2.status);
            #endif

            memory_instructions += memory_instructions_info[i].count;
            if (memory_instructions_info[i].read2.status == STEADY){
                integrally_steady_instructions += memory_instructions_info[i].count;
            }
            #ifdef DEBUG
            else { // == NON_LINEAR
                non_linear_instructions += memory_instructions_info[i].count;
            }
            #endif

        }

        if(memory_instructions_info[i].write.status != LEARN){
            #ifdef DEBUG
            printf("write: %lu ", memory_instructions_info[i].write.stride);
            display_status(memory_instructions_info[i].write.status);
            #endif

            memory_instructions += memory_instructions_info[i].count;
            if (memory_instructions_info[i].write.status == STEADY){
                integrally_steady_instructions += memory_instructions_info[i].count;
            }
            #ifdef DEBUG
            else { // == NON_LINEAR
                non_linear_instructions += memory_instructions_info[i].count;
            }
            #endif
        }

        #ifdef DEBUG
        printf("count: %lu ", memory_instructions_info[i].count);
        printf("\n");
        #endif
    }

    printf("\n");
    printf("memory_instructions_fetched: %lu\n", memory_instructions);
    printf("integrally_steady_instructions: %lu\n", integrally_steady_instructions);
    printf("memory_accesses: %lu\n", memory_instructions);
    printf("steady_memory_accesses: %lu\n", integrally_steady_instructions);
    #ifdef DEBUG
    printf("non_linear_instructions: %lu\n", non_linear_instructions);
    #endif

    return(EXIT_SUCCESS);
}