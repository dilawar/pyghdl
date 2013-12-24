--------------------------------------------------------------------------------
-- This testbench is automatically generated. May not work.
-- A file called vector.test must be generated in the same directory where
-- this testbench is saved. Each value must be separed by a space. 

-- time [in_port ] [out_port] 
-- They must be in the same order in which they appear in entity.
--------------------------------------------------------------------------------
LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE std.textio.ALL;
USE work.ALL;

-- this function converts a given string to std-logic-vector.
function to_std_logic(c: character) return std_logic is 
    variable sl: std_logic;
    begin
      case c is
        when 'U' => 
           sl := 'U'; 
        when 'X' =>
           sl := 'X';
        when '0' => 
           sl := '0';
        when '1' => 
           sl := '1';
        when 'Z' => 
           sl := 'Z';
        when 'W' => 
           sl := 'W';
        when 'L' => 
           sl := 'L';
        when 'H' => 
           sl := 'H';
        when '-' => 
           sl := '-';
        when others =>
           sl := 'X'; 
    end case;
   return sl;
  end to_std_logic;


-- converts a string into std_logic_vector

function to_std_logic_vector(s: string) return std_logic_vector is 
  variable slv: std_logic_vector(s'high-s'low downto 0);
  variable k: integer;
begin
   k := s'high-s'low;
  for i in s'range loop
     slv(k) := to_std_logic(s(i));
     k      := k - 1;
  end loop;
  return slv;
end to_std_logic_vector;                                       



ENTITY tb_{0} IS END;
ARCHITECTURE arch OF tb_{0} IS
    ----------------------------------------------------------
    -- Component declaration.
    ----------------------------------------------------------
    COMPONENT PipelinedMux 

    PORT(
merge_data_in : in std_logic_vector((g_data_width*g_number_of_inputs)-1 downto 0);
        merge_req_in : in std_logic_vector(g_number_of_inputs-1 downto 0);
        merge_ack_out : out std_logic_vector(g_number_of_inputs-1 downto 0);
        merge_data_out : out std_logic_vector(g_data_width-1 downto 0);
        merge_req_out : out std_logic;
        merge_ack_in : in std_logic;
        clock : in std_logic;
        reset : in std_logic
    );
    END COMPONENT;
        -- Signals in entity
    SIGNAL merge_data_in : std_logic_vector((g_data_width*g_number_of_inputs)-1 downto 0);
    SIGNAL merge_req_in : std_logic_vector(g_number_of_inputs-1 downto 0);
    SIGNAL merge_ack_out : std_logic_vector(g_number_of_inputs-1 downto 0);
    SIGNAL merge_data_out : std_logic_vector(g_data_width-1 downto 0);
    SIGNAL merge_req_out : std_logic;
    SIGNAL merge_ack_in : std_logic;
    SIGNAL clock : std_logic;
    SIGNAL reset : std_logic;

BEGIN
    -- Instantiate a dut 
    dut : PipelinedMux
    PORT MAP ( merge_data_in => merge_data_in,
        merge_req_in => merge_req_in,
        merge_ack_out => merge_ack_out,
        merge_data_out => merge_data_out,
        merge_req_out => merge_req_out,
        merge_ack_in => merge_ack_in,
        clock => clock,
        reset => reset
    );

    test : PROCESS 
        -- Declare variables to store the values stored in test files.
        VARIABLE tmp_merge_data_in :  std_logic_vector((g_data_width*g_number_of_inputs)-1 downto 0);
        VARIABLE tmp_merge_req_in :  std_logic_vector(g_number_of_inputs-1 downto 0);
        VARIABLE tmp_merge_ack_out :  std_logic_vector(g_number_of_inputs-1 downto 0);
        VARIABLE tmp_merge_data_out :  std_logic_vector(g_data_width-1 downto 0);
        VARIABLE tmp_merge_req_out :  std_logic;
        VARIABLE tmp_merge_ack_in :  std_logic;
        VARIABLE tmp_clock :  std_logic;
        VARIABLE tmp_reset :  std_logic;

        -- File and its minions.
        FILE vector_file : TEXT OPEN read_mode IS "./test/memory_subsystem/unordered/work/vector.test";
        VARIABLE l : LINE;
        VARIABLE r : REAL;
        VARIABLE vector_time : TIME;
        VARIABLE space : CHARACTER;
        VARIABLE good_number, good_val : BOOLEAN;
    BEGIN
        WHILE NOT endfile(vector_file) LOOP 
            readline(vector_file, l);
            -- Read the time from the begining of the line.Skip the line if it doesn't
            -- start with a number.
            read(l, r);
            NEXT WHEN NOT good_number;
            -- Convert real number to time
            vector_time := r*1 ns;
            IF (now < vector_time) THEN
            WAIT FOR vector_time - now;
            END IF;
            -- Skip a space
            read(l, space);
            -- Read other singals etc.

            -- read merge_data_in value
            read(l, tmp_merge_data_in);
            assert good_val REPORT "bad merge_data_in value";
            read(l, space); -- skip a space

            -- read merge_req_in value
            read(l, tmp_merge_req_in);
            assert good_val REPORT "bad merge_req_in value";
            read(l, space); -- skip a space

            -- read merge_ack_out value
            read(l, tmp_merge_ack_out);
            assert good_val REPORT "bad merge_ack_out value";
            assert tmp_merge_ack_out = merge_ack_out REPORT "vector mismatch";
            read(l, space); -- skip a space

            -- read merge_data_out value
            read(l, tmp_merge_data_out);
            assert good_val REPORT "bad merge_data_out value";
            assert tmp_merge_data_out = merge_data_out REPORT "vector mismatch";
            read(l, space); -- skip a space

            -- read merge_req_out value
            read(l, tmp_merge_req_out);
            assert good_val REPORT "bad merge_req_out value";
            assert tmp_merge_req_out = merge_req_out REPORT "vector mismatch";
            read(l, space); -- skip a space

            -- read merge_ack_in value
            read(l, tmp_merge_ack_in);
            assert good_val REPORT "bad merge_ack_in value";
            read(l, space); -- skip a space

            -- read clock value
            read(l, tmp_clock);
            assert good_val REPORT "bad clock value";
            read(l, space); -- skip a space

            -- read reset value
            read(l, tmp_reset);
            assert good_val REPORT "bad reset value";
            read(l, space); -- skip a space


            -- Assign temp signals to ports 
            merge_data_in <= tmp_merge_data_in;
            merge_req_in <= tmp_merge_req_in;
            merge_ack_out <= tmp_merge_ack_out;
            merge_data_out <= tmp_merge_data_out;
            merge_req_out <= tmp_merge_req_out;
            merge_ack_in <= tmp_merge_ack_in;
            clock <= tmp_clock;
            reset <= tmp_reset;

)
        END LOOP;
        ASSERT false REPORT "Test complete";
        WAIT;
    END PROCESS;
END ARCHITECTURE arch;
-- Testbech ends here.