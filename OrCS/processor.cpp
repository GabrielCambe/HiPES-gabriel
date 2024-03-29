#include "simulator.hpp"

// =====================================================================
processor_t::processor_t() {

};

// =====================================================================
void processor_t::allocate() {

};

// =====================================================================
void processor_t::clock() {

	/// Get the next instruction from the trace
	opcode_package_t new_instruction;
	if (!orcs_engine.trace_reader->trace_fetch(&new_instruction)) {
		/// If EOF
		orcs_engine.simulator_alive = false;
	}
	orcs_engine.trace_reader->current_instruction = &new_instruction;

};

// =====================================================================
void processor_t::statistics() {
	ORCS_PRINTF("######################################################\n");
	ORCS_PRINTF("processor_t\n");

};
