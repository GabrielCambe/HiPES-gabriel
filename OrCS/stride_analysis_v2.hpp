#include <stdio.h>
#include <stdlib.h>     /* malloc, free, realloc, abs */
#include <inttypes.h>
#include <assert.h>     /* assert */


//////////// Código associado ao status ////////////
enum status_t {
    UNINITIALIZED,
    LEARN,
    STEADY,
    NON_LINEAR
};

void display_status(status_t status) {
    switch (status) {
        case UNINITIALIZED:
            printf("UNINITIALIZED\n");
            break;
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

// Máquina de estados do status, com possibilidade de recuperação do estado de Non-Linear
class StatusMachine {
    public:
        status_t current_status;
        bool first_address;
        bool first_stride;
        int64_t eqCount;
        int64_t last_stride;

        StatusMachine(){
            current_status = UNINITIALIZED;
            first_address = true;
            first_stride = false;
            eqCount = 0;
            last_stride = 0;
        }

        status_t update(int64_t stride) {
            switch (current_status) {
                case LEARN:
                case UNINITIALIZED:
                case NON_LINEAR:
                    if (first_address){
                        first_address = false;
                        first_stride = true;
                        current_status = LEARN;
                    }
                    
                    if (first_stride){
                        first_stride = false;
                        current_status = STEADY;
                    }

                    if (last_stride == stride) {
                        eqCount++;
                        if (eqCount == 4){
                            eqCount = 0;
                            current_status = STEADY;
                        } else {
                            current_status = LEARN;
                        }
                    }
                    last_stride = stride;
                    break;

                case STEADY:
                    if (last_stride != stride) {
                        current_status = NON_LINEAR;
                    }
                    last_stride = stride; 
                    break;
            }
            return current_status;
        }
};

//////////// Mecanismo para analise dos strides ////////////
typedef struct {
    uint64_t first_address;
    uint64_t last_address;
    int64_t stride;
    status_t status;
    uint64_t count;
    bool integrally_steady;
}MemoryAccessInfo;

void updateAccessInfo(MemoryAccessInfo *memory_access_info, uint64_t address, StatusMachine *status_state_machine) {
    int64_t stride = address - memory_access_info->last_address;
    memory_access_info->last_address = address;
    memory_access_info->stride = stride;
    memory_access_info->status = status_state_machine->update(stride);
    if(memory_access_info->status == NON_LINEAR){
        memory_access_info->integrally_steady = false;
    }
    return;
}

typedef struct {
    uint64_t opcode_address;
    MemoryAccessInfo read;
    StatusMachine read_status;
    MemoryAccessInfo read2;
    StatusMachine read2_status;
    MemoryAccessInfo write;
    StatusMachine write_status;
    MemoryAccessInfo instruction;
    StatusMachine status;
} MemoryInstructionInfo;

void updateMemoryInfo(MemoryAccessInfo *memory_access_info, uint64_t address, StatusMachine *status_state_machine, uint64_t* partially_steady_accesses, uint64_t* total_memory_accesses) {
    if (memory_access_info->status == UNINITIALIZED) {
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
#define ASSOCIATIVITY 4
#define SETS 17
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
        (*memory_instructions_info)[i] = (CacheCell*) malloc(sizeof(CacheCell) * (2 << ASSOCIATIVITY));

        for (uint64_t j = 0; j < (2 << ASSOCIATIVITY); j++) {
            (*memory_instructions_info)[i][j].tag = 0;

            (*memory_instructions_info)[i][j].info.read.count = 0;
            (*memory_instructions_info)[i][j].info.read.status = UNINITIALIZED;
            (*memory_instructions_info)[i][j].info.read.integrally_steady = false;
                    
            (*memory_instructions_info)[i][j].info.read2.count = 0;
            (*memory_instructions_info)[i][j].info.read2.status = UNINITIALIZED;
            (*memory_instructions_info)[i][j].info.read2.integrally_steady = false;
                    
            (*memory_instructions_info)[i][j].info.write.count = 0;
            (*memory_instructions_info)[i][j].info.write.status = UNINITIALIZED;
            (*memory_instructions_info)[i][j].info.write.integrally_steady = false;
                    
            (*memory_instructions_info)[i][j].info.instruction.count = 0;
            (*memory_instructions_info)[i][j].info.instruction.status = UNINITIALIZED;
            (*memory_instructions_info)[i][j].info.instruction.integrally_steady = false;
        }
    }
    return;
}
