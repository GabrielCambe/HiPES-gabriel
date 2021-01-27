#include "simulator.hpp"
orcs_engine_t orcs_engine;

// =============================================================================
#include <stdlib.h>     /* malloc, free, realloc */
#include <inttypes.h>
#include "stride_analysis.hpp"

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

    CacheCell **memory_instructions_info = NULL; allocate_cache(&memory_instructions_info);
    MemoryInstructionInfo *instruction_info = NULL;
    uint64_t* tag = NULL;
    uint64_t cache_conflicts = 0;
    bool cache_miss = false;    

    uint64_t memory_instructions_fetched = 0;
    uint64_t memory_instructions_analysed = 0;

    uint64_t total_memory_accesses = 0; // individual accesses from instructions
    uint64_t partially_steady_accesses = 0;
    uint64_t partially_steady_instruction_accesses = 0;
    // =============================================================================

    /// Start CLOCK for all the components
    while (orcs_engine.simulator_alive) {
        orcs_engine.processor->clock();
        orcs_engine.global_cycle++;

        // =============================================================================
        is_read = orcs_engine.trace_reader->current_instruction->is_read;
        is_read2 = orcs_engine.trace_reader->current_instruction->is_read2;
        is_write = orcs_engine.trace_reader->current_instruction->is_write;
        
        if ( is_read || is_read2 || is_write ) { // É uma instrução de memória 

            current.opcode_address = orcs_engine.trace_reader->current_instruction->opcode_address;
            read_address = orcs_engine.trace_reader->current_instruction->read_address;
            read2_address = orcs_engine.trace_reader->current_instruction->read2_address;
            write_address = orcs_engine.trace_reader->current_instruction->write_address;
            memory_instructions_fetched++;

            instruction_info = &(memory_instructions_info[current.cache.set][current.cache.offset].info);
            tag = &(memory_instructions_info[current.cache.set][current.cache.offset].tag);

            if ((*tag) == 0){ // O campo da cache não foi inicializado
                (*tag) = current.cache.tag;
                instruction_info->opcode_address = current.opcode_address;

            } else {
                if ((*tag) != current.cache.tag) { // O campo foi inicializado e a tag corrente é diferente
                    cache_conflicts++;
                    cache_miss = true;
                }             
            }

            if (!cache_miss) {

                if ( is_read ) {
                    if (instruction_info->read.status == LEARN) {
                        instruction_info->read.first_address = read_address;
                        instruction_info->read.last_address = read_address;
                        instruction_info->read.status = instruction_info->read_status.update(0);

                    } else {
                        updateAccessInfo(
                            &(instruction_info->read),
                            read_address,
                            &(instruction_info->read_status)
                        );

                        if(instruction_info->read_status.current_status == STEADY)
                            partially_steady_accesses++;
                    }

                    instruction_info->read.count++;
                    // if(instruction_info->read_status.current_status == STEADY)
                    //     partially_steady_accesses++;

                    total_memory_accesses++;
                }
                
                if ( is_read2 ) {
                    if (instruction_info->read2.status == LEARN) {
                        instruction_info->read2.first_address = read2_address;
                        instruction_info->read2.last_address = read2_address;
                        instruction_info->read2.status = instruction_info->read2_status.update(0);

                        
                    } else {
                        updateAccessInfo(
                            &(instruction_info->read2),
                            read2_address,
                            &(instruction_info->read2_status)
                        );

                        if(instruction_info->read2_status.current_status == STEADY)
                            partially_steady_accesses++;
                    }

                    instruction_info->read2.count++;
                    // if(instruction_info->read2_status.current_status == STEADY)
                    //     partially_steady_accesses++;
                
                    total_memory_accesses++;
                }

                if ( is_write ) {
                    if (instruction_info->write.status == LEARN) {
                        instruction_info->write.first_address = write_address;
                        instruction_info->write.last_address = write_address;
                        instruction_info->write.status = instruction_info->write_status.update(0);

                    } else {
                        updateAccessInfo(
                            &(instruction_info->write),
                            write_address,
                            &(instruction_info->write_status)
                        );

                        if(instruction_info->write_status.current_status == STEADY)
                            partially_steady_accesses++;
                    }

                    instruction_info->write.count++;
                    // if(instruction_info->write_status.current_status == STEADY)
                    //     partially_steady_accesses++;

                    total_memory_accesses++;
                }

                if (instruction_info->instruction.status == LEARN) {
                    if ( is_read ) {                        
                        instruction_info->instruction.first_address = read_address;
                        instruction_info->instruction.last_address = read_address;
                        instruction_info->instruction.status = instruction_info->status.update(0);
                    }

                    if ( is_read2 ) {
                        instruction_info->instruction.first_address = read2_address;
                        instruction_info->instruction.last_address = read2_address;
                        instruction_info->instruction.status = instruction_info->status.update(0);
                    }

                    if ( is_write ) {
                        instruction_info->instruction.first_address = write_address;
                        instruction_info->instruction.last_address = write_address;
                        instruction_info->instruction.status = instruction_info->status.update(0);
                    }

                } else {
                    if ( is_read ) {
                        updateAccessInfo(
                            &(instruction_info->instruction),
                            read_address,
                            &(instruction_info->status)
                        );
                    }

                    if ( is_read2 ) {
                        updateAccessInfo(
                            &(instruction_info->instruction),
                            read2_address,
                            &(instruction_info->status)
                        );
                    }

                    if ( is_write ) {
                        updateAccessInfo(
                            &(instruction_info->instruction),
                            write_address,
                            &(instruction_info->status)
                        );
                    }
                    
                    if(instruction_info->status.current_status == STEADY)
                        partially_steady_instruction_accesses++;
                }

                instruction_info->count++;
                // if(instruction_info->status.current_status == STEADY)
                //     partially_steady_instruction_accesses++;

                memory_instructions_analysed++;
            }
            cache_miss = false;
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
    uint64_t integrally_steady_instruction_accesses = 0;
    uint64_t integrally_steady_accesses = 0;

    for (uint64_t i = 0; i < (2 << 18); i++){
        for (uint64_t j = 0; j < 8; j++){
            if (memory_instructions_info[i][j].tag != 0) {
                if(memory_instructions_info[i][j].info.read.status != LEARN){
                    read_accesses += memory_instructions_info[i][j].info.read.count;
                    if (memory_instructions_info[i][j].info.read.status == STEADY){
                        integrally_steady_accesses += memory_instructions_info[i][j].info.read.count;
                    }
                }

                if(memory_instructions_info[i][j].info.read2.status != LEARN){
                    read2_accesses += memory_instructions_info[i][j].info.read2.count;
                    if (memory_instructions_info[i][j].info.read2.status == STEADY){
                        integrally_steady_accesses += memory_instructions_info[i][j].info.read2.count;
                    }
                }

                if(memory_instructions_info[i][j].info.write.status != LEARN){
                    write_accesses += memory_instructions_info[i][j].info.write.count;
                    if (memory_instructions_info[i][j].info.write.status == STEADY){
                        integrally_steady_accesses += memory_instructions_info[i][j].info.write.count;
                    }
                }
           
                if(memory_instructions_info[i][j].info.instruction.status != LEARN){
                    memory_instructions_counted += memory_instructions_info[i][j].info.count;
                    if (memory_instructions_info[i][j].info.instruction.status == STEADY){
                        integrally_steady_instruction_accesses += memory_instructions_info[i][j].info.count;
                    }
                    
                }
            }
        }
    }

    printf("\n");
    printf("memory_instructions_analysed: %lu\n", memory_instructions_analysed);
    printf("cache_conflicts: %lu\n", cache_conflicts);
    printf("memory_instructions_fetched: %lu\n", memory_instructions_fetched);

    printf("read_accesses: %lu\n", read_accesses);
    printf("read2_accesses: %lu\n", read2_accesses);
    printf("write_accesses: %lu\n", write_accesses);
    printf("memory_accesses: %lu\n", total_memory_accesses);

    printf("memory_instructions_counted: %lu\n", memory_instructions_counted);
    printf("integrally_steady_instruction_accesses: %lu\n", integrally_steady_instruction_accesses);
    printf("partially_steady_instruction_accesses: %lu\n", partially_steady_instruction_accesses);

    printf("partially_steady_accesses: %lu\n", partially_steady_accesses);
    printf("integrally_steady_accesses: %lu\n", integrally_steady_accesses);

    return(EXIT_SUCCESS);
}