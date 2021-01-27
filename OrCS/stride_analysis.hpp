#include <stdio.h>
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
        uint64_t stride = 0;
        status_t status = LEARN;
        uint64_t count = 0;

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
        MemoryAccessInfo instruction;
        StatusMachine status;
        uint64_t count = 0;

};

struct CacheCell {
    u_int64_t tag;
    MemoryInstructionInfo info;
};

// Union para interpretar um endereço de 64 bits como o endereço de uma cache conjunto associativo com 2^18 conjuntos e 8 vias
typedef union {
    uint64_t opcode_address;
    struct {
        uint64_t offset:3;
        uint64_t set:18;
        uint64_t tag:43;
    } cache;
} instruction_address;

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

void allocate_cache(CacheCell ***memory_instructions_info) {
    (*memory_instructions_info) = (CacheCell **) malloc(sizeof(CacheCell*) * (2 << 18));
    for (uint64_t i = 0; i < (2 << 18); i++) {
        (*memory_instructions_info)[i] = (CacheCell*) malloc(sizeof(CacheCell) * 8);
        (*memory_instructions_info)[i]->tag = 2 << 43;
    }
    return;
}