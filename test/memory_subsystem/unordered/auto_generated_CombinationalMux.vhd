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
    COMPONENT CombinationalMux 

    GENERIC(
    g_data_width       : integer := 32;
    g_number_of_inputs: integer := 2
    );
    PORT(
in_data : in std_logic_vector(( 32* 2)-1 downto 0);
        out_data : out std_logic_vector( 32-1 downto 0);
        in_req : in std_logic_vector( 2-1 downto 0);
        in_ack : out std_logic_vector( 2-1 downto 0);
        out_req : out std_logic;
        out_ack : in std_logic
    );
    END COMPONENT;
        -- Signals in entity
    SIGNAL in_data : std_logic_vector(( 32* 2)-1 downto 0);
    SIGNAL out_data : std_logic_vector( 32-1 downto 0);
    SIGNAL in_req : std_logic_vector( 2-1 downto 0);
    SIGNAL in_ack : std_logic_vector( 2-1 downto 0);
    SIGNAL out_req : std_logic;
    SIGNAL out_ack : std_logic;

BEGIN
    -- Instantiate a dut 
    dut : CombinationalMux
    GENERIC MAP(    g_data_width =>  32,
        g_number_of_inputs =>  2)
    PORT MAP ( in_data => in_data,
        out_data => out_data,
        in_req => in_req,
        in_ack => in_ack,
        out_req => out_req,
        out_ack => out_ack
    );

    test : PROCESS 
        -- Declare variables to store the values stored in test files.
        VARIABLE tmp_in_data :  std_logic_vector(( 32* 2)-1 downto 0);
        VARIABLE tmp_out_data :  std_logic_vector( 32-1 downto 0);
        VARIABLE tmp_in_req :  std_logic_vector( 2-1 downto 0);
        VARIABLE tmp_in_ack :  std_logic_vector( 2-1 downto 0);
        VARIABLE tmp_out_req :  std_logic;
        VARIABLE tmp_out_ack :  std_logic;

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

            -- read in_data value
            read(l, tmp_in_data);
            assert good_val REPORT "bad in_data value";
            read(l, space); -- skip a space

            -- read out_data value
            read(l, tmp_out_data);
            assert good_val REPORT "bad out_data value";
            assert tmp_out_data = out_data REPORT "vector mismatch";
            read(l, space); -- skip a space

            -- read in_req value
            read(l, tmp_in_req);
            assert good_val REPORT "bad in_req value";
            read(l, space); -- skip a space

            -- read in_ack value
            read(l, tmp_in_ack);
            assert good_val REPORT "bad in_ack value";
            assert tmp_in_ack = in_ack REPORT "vector mismatch";
            read(l, space); -- skip a space

            -- read out_req value
            read(l, tmp_out_req);
            assert good_val REPORT "bad out_req value";
            assert tmp_out_req = out_req REPORT "vector mismatch";
            read(l, space); -- skip a space

            -- read out_ack value
            read(l, tmp_out_ack);
            assert good_val REPORT "bad out_ack value";
            read(l, space); -- skip a space


            -- Assign temp signals to ports 
            in_data <= tmp_in_data;
            out_data <= tmp_out_data;
            in_req <= tmp_in_req;
            in_ack <= tmp_in_ack;
            out_req <= tmp_out_req;
            out_ack <= tmp_out_ack;

)
        END LOOP;
        ASSERT false REPORT "Test complete";
        WAIT;
    END PROCESS;
END ARCHITECTURE arch;
-- Testbech ends here.