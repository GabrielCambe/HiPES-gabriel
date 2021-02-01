#include <stdio.h>
#include <stdlib.h>     /* malloc, free, realloc, abs */
#include <inttypes.h>


//////////// Código associado ao status ////////////
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
        bool first_access;
        status_t current_status;
        int64_t last_stride;

        StatusMachine(){
            first_access = true;
            current_status = LEARN;
        }

        status_t update(int64_t stride) {
            if (current_status == LEARN){
                current_status = STEADY;
            } else if (current_status == STEADY){
                if (first_access || (last_stride == stride)){
                    current_status = STEADY;
                    first_access = false;
                } else {
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

//////////// Mecanismo para analise dos strides ////////////
struct MemoryAccessInfo {
    // public:
        uint64_t first_address = 0;
        uint64_t last_address = 0;
        int64_t stride = 0;
        status_t status = LEARN;
        uint64_t count = 0;

};

void updateAccessInfo(MemoryAccessInfo *memory_access_info, uint64_t address, StatusMachine *status_state_machine) {
    int64_t stride = address - memory_access_info->last_address;
    memory_access_info->last_address = address;
    memory_access_info->stride = stride;
    memory_access_info->status = status_state_machine->update(stride);
    return;
}

struct MemoryInstructionInfo {
    // public:
        uint64_t opcode_address;
        MemoryAccessInfo read;
        StatusMachine read_status;
        MemoryAccessInfo read2;
        StatusMachine read2_status;
        MemoryAccessInfo write;
        StatusMachine write_status;
        MemoryAccessInfo instruction;
        StatusMachine status;
        // uint64_t count = 0;
};

void updateMemoryInfo(MemoryAccessInfo *memory_access_info, uint64_t address, StatusMachine *status_state_machine, uint64_t* partially_steady_accesses, uint64_t* total_memory_accesses) {
    if (memory_access_info->status == LEARN) {
        memory_access_info->first_address = address;
        memory_access_info->last_address = address;
        memory_access_info->status = status_state_machine->update(0);

    } else {
        updateAccessInfo(
            memory_access_info,
            address,
            status_state_machine

        );

        if(status_state_machine->current_status == STEADY)
            (*partially_steady_accesses)++;
    }

    memory_access_info->count++;
 
    (*total_memory_accesses)++;
    
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

//////////// Mecanismo para guardar as informações obtidas, evitando o baixo desempenho de repetidos mallocs ////////////
#define ASSOCIATIVITY 3
#define SETS 18
#define TAG 43
// Union para interpretar um endereço de 64 bits como o endereço de uma cache conjunto associativo com 2^SETS conjuntos e 2^ASSOCIATIVITY vias
typedef union {
    uint64_t opcode_address;
    struct {
        uint64_t offset:ASSOCIATIVITY;
        uint64_t set:SETS;
        uint64_t tag:TAG;
    } cache;
} instruction_address;

struct CacheCell {
    u_int64_t tag;
    MemoryInstructionInfo info;
};

void allocate_cache(CacheCell ***memory_instructions_info) {
    (*memory_instructions_info) = (CacheCell **) malloc(sizeof(CacheCell*) * (2 << SETS));
    for (uint64_t i = 0; i < (2 << SETS); i++) {
        (*memory_instructions_info)[i] = (CacheCell*) malloc(sizeof(CacheCell) * 2 << ASSOCIATIVITY);
        (*memory_instructions_info)[i]->tag = 0;
    }
    return;
}
