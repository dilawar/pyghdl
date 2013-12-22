
ENTITY tb_demerge_tree IS END;
-------------------------------------------------------------------------------
-- This testbench is automatically generated. May not work.
-- A file called vector.test must be generated in the same directory where
-- this testbench is saved. Each value must be separed by a space. 

-- time [in_port ] [out_port] 
-- They must be in the same order in which they appear in entity.
-------------------------------------------------------------------------------
LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE std.textio.ALL;
USE work.ALL;

ARCHITECTURE arch OF tb_demerge_tree IS 

	----------------------------------------------------------------
	-- Component declaration.
	----------------------------------------------------------------
	COMPONENT demerge_tree 
		PORT ( 
		demerge_data_out : out std_logic_vector((g_data_width*g_number_of_outputs)-1 downto 0);
		demerge_ready_out : out std_logic_vector(g_number_of_outputs-1 downto 0);
		demerge_accept_in : in std_logic_vector(g_number_of_outputs-1 downto 0);
		demerge_data_in : in std_logic_vector(g_data_width-1 downto 0);
		demerge_ack_out : out std_logic;
		demerge_req_in : in std_logic;
		demerge_sel_in : in std_logic_vector(g_id_width-1 downto 0);
		clock : in std_logic;
		reset : in std_logic);
	END COMPONENT;
	
	-- Signals in entity 
	SIGNAL demerge_data_out :  std_logic_vector((g_data_width*g_number_of_outputs)-1 downto 0);
	SIGNAL demerge_ready_out :  std_logic_vector(g_number_of_outputs-1 downto 0);
	SIGNAL demerge_accept_in :  std_logic_vector(g_number_of_outputs-1 downto 0);
	SIGNAL demerge_data_in :  std_logic_vector(g_data_width-1 downto 0);
	SIGNAL demerge_ack_out :  std_logic;
	SIGNAL demerge_req_in :  std_logic;
	SIGNAL demerge_sel_in :  std_logic_vector(g_id_width-1 downto 0);
	SIGNAL clock :  std_logic;
	SIGNAL reset :  std_logic;

BEGIN
	-- Instantiate a dut 
	dut : demerge_tree PORT MAP( 
		demerge_data_out => demerge_data_out,
		demerge_ready_out => demerge_ready_out,
		demerge_accept_in => demerge_accept_in,
		demerge_data_in => demerge_data_in,
		demerge_ack_out => demerge_ack_out,
		demerge_req_in => demerge_req_in,
		demerge_sel_in => demerge_sel_in,
		clock => clock,
		reset => reset);
	test : PROCESS 
		-- Declare variables to store the values stored in test files. 
		VARIABLE tmp_demerge_data_out :  std_logic_vector((g_data_width*g_number_of_outputs)-1 downto 0);
		VARIABLE tmp_demerge_ready_out :  std_logic_vector(g_number_of_outputs-1 downto 0);
		VARIABLE tmp_demerge_accept_in :  std_logic_vector(g_number_of_outputs-1 downto 0);
		VARIABLE tmp_demerge_data_in :  std_logic_vector(g_data_width-1 downto 0);
		VARIABLE tmp_demerge_ack_out :  std_logic;
		VARIABLE tmp_demerge_req_in :  std_logic;
		VARIABLE tmp_demerge_sel_in :  std_logic_vector(g_id_width-1 downto 0);
		VARIABLE tmp_clock :  std_logic;
		VARIABLE tmp_reset :  std_logic;

		-- File and its minions.
		FILE vector_file : TEXT OPEN read_mode IS "test/memory_subsystem/strictly_ordered//work/vector.test";
		VARIABLE l : LINE;
		VARIABLE r : REAL;
		VARIABLE vector_time : TIME;
		VARIABLE space : CHARACTER;
		VARIABLE good_number, good_val : BOOLEAN;
	BEGIN
		WHILE NOT endfile(vector_file) LOOP 
			readline(vector_file, l);
			-- Read the time from the begining of the line. Skip the line if it doesn't
			-- start with a number.
			read(l, r, good => good_number);
			NEXT WHEN NOT good_number;
			-- Convert real number to time
			vector_time := r*1 ns;
			IF (now < vector_time) THEN
			WAIT FOR vector_time - now;
			END IF;
			-- Skip a space
			read(l, space);
			-- Read other singals etc. 
			-- read demerge_data_out value
			read(l, tmp_demerge_data_out, good_val);
			assert good_val REPORT "bad demerge_data_out value";
			assert tmp_demerge_data_out = demerge_data_out REPORT "vector mismatch";
			read(l, space); -- skip a space

			-- read demerge_ready_out value
			read(l, tmp_demerge_ready_out, good_val);
			assert good_val REPORT "bad demerge_ready_out value";
			assert tmp_demerge_ready_out = demerge_ready_out REPORT "vector mismatch";
			read(l, space); -- skip a space

			-- read demerge_accept_in value
			read(l, tmp_demerge_accept_in, good_val);
			assert good_val REPORT "bad demerge_accept_in value";
			read(l, space); -- skip a space

			-- read demerge_data_in value
			read(l, tmp_demerge_data_in, good_val);
			assert good_val REPORT "bad demerge_data_in value";
			read(l, space); -- skip a space

			-- read demerge_ack_out value
			read(l, tmp_demerge_ack_out, good_val);
			assert good_val REPORT "bad demerge_ack_out value";
			assert tmp_demerge_ack_out = demerge_ack_out REPORT "vector mismatch";
			read(l, space); -- skip a space

			-- read demerge_req_in value
			read(l, tmp_demerge_req_in, good_val);
			assert good_val REPORT "bad demerge_req_in value";
			read(l, space); -- skip a space

			-- read demerge_sel_in value
			read(l, tmp_demerge_sel_in, good_val);
			assert good_val REPORT "bad demerge_sel_in value";
			read(l, space); -- skip a space

			-- read clock value
			read(l, tmp_clock, good_val);
			assert good_val REPORT "bad clock value";
			read(l, space); -- skip a space

			-- read reset value
			read(l, tmp_reset, good_val);
			assert good_val REPORT "bad reset value";
			read(l, space); -- skip a space


			-- Assign temp signals to ports 
			demerge_data_out <= tmp_demerge_data_out;
			demerge_ready_out <= tmp_demerge_ready_out;
			demerge_accept_in <= tmp_demerge_accept_in;
			demerge_data_in <= tmp_demerge_data_in;
			demerge_ack_out <= tmp_demerge_ack_out;
			demerge_req_in <= tmp_demerge_req_in;
			demerge_sel_in <= tmp_demerge_sel_in;
			clock <= tmp_clock;
			reset <= tmp_reset;

		END LOOP;
		ASSERT false REPORT "Test complete";
		WAIT;
	END PROCESS;
END ARCHITECTURE arch;
-- Testbech ends here.
  