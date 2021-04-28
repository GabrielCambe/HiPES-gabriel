#include "simulator.hpp"
orcs_engine_t orcs_engine;

// =============================================================================
#include <stdlib.h>     /* malloc, free, realloc */
#include <inttypes.h>
#include "stride_analysis_v2.hpp"

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
    bool is_read, is_read2, is_write;
    instruction_address current;
    uint64_t read_address;
    uint64_t read2_address;
    uint64_t write_address;
    int64_t stride;

    CacheCell **memory_instructions_info = NULL; allocate_cache(&memory_instructions_info);
    MemoryInstructionInfo *instruction_info = NULL;
    uint64_t* tag = NULL;
    uint64_t cache_conflicts = 0;
    bool cache_hit = false;    

    uint64_t memory_instructions_fetched = 0;
    uint64_t memory_instructions_analysed = 0;

    uint64_t total_memory_accesses = 0; // individual accesses from instructions
    uint64_t partially_steady_accesses = 0;
    uint64_t partially_steady_instructions = 0;
    bool already_incremented_partially_steady_instructions = false;
    // =============================================================================

    /// Start CLOCK for all the components
    while (orcs_engine.simulator_alive) {
        orcs_engine.processor->clock();
        orcs_engine.global_cycle++;

        // =============================================================================
        current.opcode_address = orcs_engine.trace_reader->current_instruction->opcode_address;
        
        is_read = orcs_engine.trace_reader->current_instruction->is_read;
        read_address = orcs_engine.trace_reader->current_instruction->read_address;
        is_read2 = orcs_engine.trace_reader->current_instruction->is_read2;
        read2_address = orcs_engine.trace_reader->current_instruction->read2_address;
        is_write = orcs_engine.trace_reader->current_instruction->is_write;
        write_address = orcs_engine.trace_reader->current_instruction->write_address;

        memory_instructions_fetched += 1;

        if (is_read == true){
            assert(read_address != 0);
        }
        
        if (is_read2 == true){
            assert(read2_address != 0);
        }
        
        if (is_write == true){
            assert(write_address != 0);
        }
        
        if ( (is_read == true) || (is_read2 == true) || (is_write == true) ) { // É uma instrução de memória 
            tag = &(memory_instructions_info[current.cache.set][current.cache.offset].tag);

            if ((*tag) == 0 && current.cache.tag != 0){ // O campo da cache não foi inicializado
                (*tag) = current.cache.tag;

                instruction_info = &(memory_instructions_info[current.cache.set][current.cache.offset].info);
                instruction_info->opcode_address = current.opcode_address;
                cache_hit = true;
                
            } else {
                if ((*tag) != current.cache.tag || current.cache.tag == 0){ // O campo foi inicializado e a tag corrente é diferente ou a tag corrente é igual à zero
                    cache_conflicts += 1;
                    cache_hit = false;
                } else {
                    cache_hit = true;
                } 
            }


            if (cache_hit == true) {
                if ( is_read == true ) {
                    if (instruction_info->read.status == UNINITIALIZED) {
                        instruction_info->read.first_address = read_address;
                        instruction_info->read.last_address = read_address;
                        instruction_info->read.status = instruction_info->read_status.update(0);
                        // display_status(instruction_info->read.status);
                        instruction_info->read.integrally_steady = true;          

                    } else {
                        stride = instruction_info->read.last_address - read_address;
                        instruction_info->read.stride = stride;
                        instruction_info->read.status = instruction_info->read_status.update(stride);
                        // display_status(instruction_info->read.status);
                        instruction_info->read.last_address = read_address;

                        if(instruction_info->read.status == STEADY){
                            partially_steady_accesses += 1;
                        } else if (instruction_info->read.status == NON_LINEAR){
                            instruction_info->read.integrally_steady = false;

                        }
                    }
                    
                    instruction_info->read.count += 1; 
                    total_memory_accesses += 1;

                    if (instruction_info->instruction.status == UNINITIALIZED) {
                        instruction_info->instruction.first_address = read_address;
                        instruction_info->instruction.last_address = read_address;
                        instruction_info->instruction.status = instruction_info->status.update(0);
                        instruction_info->instruction.integrally_steady = true;

                    } else {
                        stride = instruction_info->instruction.last_address - read_address;
                        instruction_info->instruction.stride = stride;
                        instruction_info->instruction.status = instruction_info->status.update(stride);
                        instruction_info->instruction.last_address = read_address;

                        if (instruction_info->instruction.status == NON_LINEAR){
                            instruction_info->instruction.integrally_steady = false;
                        } else if (instruction_info->instruction.status == STEADY && !already_incremented_partially_steady_instructions){
                            partially_steady_instructions += 1;
                            already_incremented_partially_steady_instructions = true;
                        }
                    }
                }
                

                if ( is_read2 == true ) {
                    if (instruction_info->read2.status == UNINITIALIZED) {
                        instruction_info->read2.first_address = read2_address;
                        instruction_info->read2.last_address = read2_address;
                        instruction_info->read2.status = instruction_info->read2_status.update(0);
                        instruction_info->read2.integrally_steady = true;
                        
                    } else {
                        stride = instruction_info->read2.last_address - read2_address;
                        instruction_info->read2.stride = stride;
                        instruction_info->read2.status = instruction_info->read2_status.update(stride);
                        instruction_info->read2.last_address = read2_address;

                        if(instruction_info->read2.status == STEADY){
                            partially_steady_accesses += 1;
                        } else if (instruction_info->read2.status == NON_LINEAR){
                            instruction_info->read2.integrally_steady = false;
                        }
                    }

                    instruction_info->read2.count += 1;
                    total_memory_accesses += 1;

                    if (instruction_info->instruction.status == UNINITIALIZED) {
                        instruction_info->instruction.first_address = read2_address;
                        instruction_info->instruction.last_address = read2_address;
                        instruction_info->instruction.status = instruction_info->status.update(0);
                        instruction_info->instruction.integrally_steady = true;
            
                    } else {
                        stride = instruction_info->instruction.last_address - read2_address;
                        instruction_info->instruction.stride = stride;
                        instruction_info->instruction.status = instruction_info->status.update(stride);
                        instruction_info->instruction.last_address = read2_address;

                        if (instruction_info->instruction.status == NON_LINEAR){
                            instruction_info->instruction.integrally_steady = false;
                        } else if (instruction_info->instruction.status == STEADY && !already_incremented_partially_steady_instructions){
                            partially_steady_instructions += 1;
                            already_incremented_partially_steady_instructions = true;
                        }
                    }
                }


                if ( is_write == true ) {
                    if (instruction_info->write.status == UNINITIALIZED) {
                        instruction_info->write.first_address = write_address;
                        instruction_info->write.last_address = write_address;
                        instruction_info->write.status = instruction_info->write_status.update(0);
                        instruction_info->write.integrally_steady = true;

                    } else {
                        stride = instruction_info->write.last_address - write_address;
                        instruction_info->write.stride = stride;
                        instruction_info->write.status = instruction_info->write_status.update(stride);
                        instruction_info->write.last_address = write_address;

                        if (instruction_info->write.status == STEADY){
                            partially_steady_accesses += 1;
                        } else if (instruction_info->write.status == NON_LINEAR){
                            instruction_info->write.integrally_steady = false;

                        }
                    }

                    instruction_info->write.count += 1;
                    total_memory_accesses += 1;

                    if (instruction_info->instruction.status == UNINITIALIZED) {
                        instruction_info->instruction.first_address = write_address;
                        instruction_info->instruction.last_address = write_address;
                        instruction_info->instruction.status = instruction_info->status.update(0);
                        instruction_info->instruction.integrally_steady = true;

                    } else {
                        stride = instruction_info->instruction.last_address - write_address;
                        instruction_info->instruction.stride = stride;
                        instruction_info->instruction.status = instruction_info->status.update(stride);
                        instruction_info->instruction.last_address = write_address;
                 
                        if (instruction_info->instruction.status == NON_LINEAR){
                            instruction_info->instruction.integrally_steady = false;
                        } else if (instruction_info->instruction.status == STEADY && !already_incremented_partially_steady_instructions){
                            partially_steady_instructions += 1;
                            already_incremented_partially_steady_instructions = true;
                        }

                    }
                }

                instruction_info->instruction.count += 1;
                memory_instructions_analysed += 1; 
                already_incremented_partially_steady_instructions = false;

                cache_hit = false;
            }
        }
        // =============================================================================
    }
	ORCS_PRINTF("\nEnd of Simulation\n")
	orcs_engine.trace_reader->statistics();
    orcs_engine.processor->statistics();

    uint64_t read_accesses = 0;
    uint64_t read2_accesses = 0;
    uint64_t write_accesses = 0;
    uint64_t memory_instructions_counted = 0;
    uint64_t integrally_steady_instructions = 0;
    uint64_t accesses_in_integrally_steady_instructions = 0;
    uint64_t integrally_steady_accesses = 0;
    uint64_t error = 0;

    for (uint64_t i = 0; i < (2 << SETS); i++){
        for (uint64_t j = 0; j < (2 << ASSOCIATIVITY); j++){
            if (memory_instructions_info[i][j].tag != 0) {
                if(memory_instructions_info[i][j].info.read.status != UNINITIALIZED){
                    read_accesses += memory_instructions_info[i][j].info.read.count;
                    if (memory_instructions_info[i][j].info.read.integrally_steady){
                        integrally_steady_accesses += memory_instructions_info[i][j].info.read.count;
                    }
                }
                
                if(memory_instructions_info[i][j].info.read2.status != UNINITIALIZED){
                    read2_accesses += memory_instructions_info[i][j].info.read2.count;
                    if (memory_instructions_info[i][j].info.read2.integrally_steady){
                        integrally_steady_accesses += memory_instructions_info[i][j].info.read2.count;
                    }
                }

                if(memory_instructions_info[i][j].info.write.status != UNINITIALIZED){
                    write_accesses += memory_instructions_info[i][j].info.write.count;
                    if (memory_instructions_info[i][j].info.write.integrally_steady){
                        integrally_steady_accesses += memory_instructions_info[i][j].info.write.count;
                    }
                }
           
                if(memory_instructions_info[i][j].info.instruction.status != UNINITIALIZED){
                    memory_instructions_counted += memory_instructions_info[i][j].info.instruction.count;

                    if (memory_instructions_info[i][j].info.instruction.integrally_steady){
                        accesses_in_integrally_steady_instructions += (memory_instructions_info[i][j].info.read.count + memory_instructions_info[i][j].info.read2.count + memory_instructions_info[i][j].info.write.count);

                        if(memory_instructions_info[i][j].info.read.count > 0) {
                            if(memory_instructions_info[i][j].info.read2.count > 0 || memory_instructions_info[i][j].info.write.count > 0) {
                                printf("\nInstrução integralmente estável tem mais de um tipo de acesso!\n");

                                printf("read:\n first_address: %" PRIu64 " last_address: %" PRIu64 " stride: %#" PRId64 " count: %" PRIu64 "\n", memory_instructions_info[i][j].info.read.first_address, memory_instructions_info[i][j].info.read.last_address, memory_instructions_info[i][j].info.read.stride, memory_instructions_info[i][j].info.read.count);

                                printf("read2:\n first_address: %" PRIu64 " last_address: %" PRIu64 " stride: %#" PRId64 " count: %" PRIu64 "\n", memory_instructions_info[i][j].info.read2.first_address, memory_instructions_info[i][j].info.read2.last_address, memory_instructions_info[i][j].info.read2.stride, memory_instructions_info[i][j].info.read2.count);

                                printf("write:\n first_address: %" PRIu64 " last_address: %" PRIu64 " stride: %#" PRId64 " count: %" PRIu64 "\n", memory_instructions_info[i][j].info.write.first_address, memory_instructions_info[i][j].info.write.last_address, memory_instructions_info[i][j].info.write.stride, memory_instructions_info[i][j].info.write.count);
                            }
                        } else if(memory_instructions_info[i][j].info.read2.count > 0) {
                            if(memory_instructions_info[i][j].info.read.count > 0 || memory_instructions_info[i][j].info.write.count > 0) {
                                printf("Instrução integralmente estável tem mais de um tipo de acesso!!\n");

                                printf("read:\n first_address: %" PRIu64 " last_address: %" PRIu64 " stride: %#" PRId64 " count: %" PRIu64 "\n", memory_instructions_info[i][j].info.read.first_address, memory_instructions_info[i][j].info.read.last_address, memory_instructions_info[i][j].info.read.stride, memory_instructions_info[i][j].info.read.count);

                                printf("read2:\n first_address: %" PRIu64 " last_address: %" PRIu64 " stride: %#" PRId64 " count: %" PRIu64 "\n", memory_instructions_info[i][j].info.read2.first_address, memory_instructions_info[i][j].info.read2.last_address, memory_instructions_info[i][j].info.read2.stride, memory_instructions_info[i][j].info.read2.count);

                                printf("write:\n first_address: %" PRIu64 " last_address: %" PRIu64 " stride: %#" PRId64 " count: %" PRIu64 "\n", memory_instructions_info[i][j].info.write.first_address, memory_instructions_info[i][j].info.write.last_address, memory_instructions_info[i][j].info.write.stride, memory_instructions_info[i][j].info.write.count);                            }
                        } else if(memory_instructions_info[i][j].info.write.count > 0) {
                            if(memory_instructions_info[i][j].info.read.count > 0 || memory_instructions_info[i][j].info.read2.count > 0) {
                                printf("Instrução integralmente estável tem mais de um tipo de acesso!!\n");

                                printf("read:\n first_address: %" PRIu64 " last_address: %" PRIu64 " stride: %#" PRId64 " count: %" PRIu64 "\n", memory_instructions_info[i][j].info.read.first_address, memory_instructions_info[i][j].info.read.last_address, memory_instructions_info[i][j].info.read.stride, memory_instructions_info[i][j].info.read.count);

                                printf("read2:\n first_address: %" PRIu64 " last_address: %" PRIu64 " stride: %#" PRId64 " count: %" PRIu64 "\n", memory_instructions_info[i][j].info.read2.first_address, memory_instructions_info[i][j].info.read2.last_address, memory_instructions_info[i][j].info.read2.stride, memory_instructions_info[i][j].info.read2.count);

                                printf("write:\n first_address: %" PRIu64 " last_address: %" PRIu64 " stride: %#" PRId64 " count: %" PRIu64 "\n", memory_instructions_info[i][j].info.write.first_address, memory_instructions_info[i][j].info.write.last_address, memory_instructions_info[i][j].info.write.stride, memory_instructions_info[i][j].info.write.count);
                            }
                        }

                        integrally_steady_instructions += memory_instructions_info[i][j].info.instruction.count;
                    }
                    
                } else {
                    error += memory_instructions_info[i][j].info.instruction.count;
                }
            }
        }
    }

    printf("\n");
    printf("%s\n",  orcs_engine.arg_trace_file_name);
    printf("memory_instructions_fetched: %" PRIu64 "\n", memory_instructions_fetched);
    // printf("a is %#" PRIx64
    //         " & b is %#" PRIx64
    //         " & c is %#" PRIx64 "\n",
    //         a, b, c);
    printf("memory_instructions_analysed: %" PRIu64 "\n", memory_instructions_analysed);
    printf("cache_conflicts: %" PRIu64 "\n", cache_conflicts);

    printf("memory_instructions_counted: %" PRIu64 "\n", memory_instructions_counted);
    printf("error: %" PRIu64 "\n", error);

    printf("partially_steady_instructions: %" PRIu64 "\n", partially_steady_instructions);
    printf("integrally_steady_instructions: %" PRIu64 "\n", integrally_steady_instructions);
    printf("accesses_in_integrally_steady_instructions: %" PRIu64 "\n", accesses_in_integrally_steady_instructions);

    printf("memory_accesses: %" PRIu64 "\n", total_memory_accesses);
    printf("read_accesses: %" PRIu64 "\n", read_accesses);
    printf("read2_accesses: %" PRIu64 "\n", read2_accesses);
    printf("write_accesses: %" PRIu64 "\n", write_accesses);

    printf("partially_steady_accesses: %" PRIu64 "\n", partially_steady_accesses);
    printf("integrally_steady_accesses: %" PRIu64 "\n", integrally_steady_accesses);

    return(EXIT_SUCCESS);
}