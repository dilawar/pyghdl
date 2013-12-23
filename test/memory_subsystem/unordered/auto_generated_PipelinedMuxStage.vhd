
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

ENTITY tb_PipelinedMuxStage IS END;
ARCHITECTURE arch OF tb_PipelinedMuxStage IS 

    ----------------------------------------------------------------
    -- Component declaration.
    ----------------------------------------------------------------
    COMPONENT PipelinedMuxStage 
    GENERIC(g_data_width: integer := 10;
           g_number_of_inputs: integer := 8;
           g_number_of_outputs: integer := 1;
           g_tag_width : integer := 3  
           
    );
    PORT(data_left : in std_logic_vector(( 10* 8)-1 downto 0);
        req_in : in std_logic_vector( 8-1 downto 0);
        ack_out : out std_logic_vector( 8-1 downto 0);
        data_right : out std_logic_vector(( 10* 1)-1 downto 0);
        req_out : out std_logic_vector( 1-1 downto 0);
        ack_in : in std_logic_vector( 1-1 downto 0);
        clock : in std_logic;
        reset : in std_logic
    );
    END COMPONENT;
    
    -- Signals in entity 
    SIGNAL data_left : std_logic_vector(( 10* 8)-1 downto 0);
    SIGNAL req_in : std_logic_vector( 8-1 downto 0);
    SIGNAL ack_out : std_logic_vector( 8-1 downto 0);
    SIGNAL data_right : std_logic_vector(( 10* 1)-1 downto 0);
    SIGNAL req_out : std_logic_vector( 1-1 downto 0);
    SIGNAL ack_in : std_logic_vector( 1-1 downto 0);
    SIGNAL clock : std_logic;
    SIGNAL reset : std_logic;

BEGIN
    -- Instantiate a dut 
    dut : PipelinedMuxStage
    GENERIC MAP(    g_data_width =>  10,
        g_number_of_inputs =>  8,
        g_number_of_outputs =>  1,
        g_tag_width =>  3)
    PORT MAP ( data_left => data_left,
        req_in => req_in,
        ack_out => ack_out,
        data_right => data_right,
        req_out => req_out,
        ack_in => ack_in,
        clock => clock,
        reset => reset
    );

    test : PROCESS 
        -- Declare variables to store the values stored in test files. 
        VARIABLE tmp_data_left :  std_logic_vector(( 10* 8)-1 downto 0);
        VARIABLE tmp_req_in :  std_logic_vector( 8-1 downto 0);
        VARIABLE tmp_ack_out :  std_logic_vector( 8-1 downto 0);
        VARIABLE tmp_data_right :  std_logic_vector(( 10* 1)-1 downto 0);
        VARIABLE tmp_req_out :  std_logic_vector( 1-1 downto 0);
        VARIABLE tmp_ack_in :  std_logic_vector( 1-1 downto 0);
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
            -- read data_left value
            read(l, tmp_data_left, good_val);
            assert good_val REPORT "bad data_left value";
            read(l, space); -- skip a space

            -- read req_in value
            read(l, tmp_req_in, good_val);
            assert good_val REPORT "bad req_in value";
            read(l, space); -- skip a space

            -- read ack_out value
            read(l, tmp_ack_out, good_val);
            assert good_val REPORT "bad ack_out value";
            assert tmp_ack_out = ack_out REPORT "vector mismatch";
            read(l, space); -- skip a space

            -- read data_right value
            read(l, tmp_data_right, good_val);
            assert good_val REPORT "bad data_right value";
            assert tmp_data_right = data_right REPORT "vector mismatch";
            read(l, space); -- skip a space

            -- read req_out value
            read(l, tmp_req_out, good_val);
            assert good_val REPORT "bad req_out value";
            assert tmp_req_out = req_out REPORT "vector mismatch";
            read(l, space); -- skip a space

            -- read ack_in value
            read(l, tmp_ack_in, good_val);
            assert good_val REPORT "bad ack_in value";
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
            data_left <= tmp_data_left;
            req_in <= tmp_req_in;
            ack_out <= tmp_ack_out;
            data_right <= tmp_data_right;
            req_out <= tmp_req_out;
            ack_in <= tmp_ack_in;
            clock <= tmp_clock;
            reset <= tmp_reset;

        END LOOP;
        ASSERT false REPORT "Test complete";
        WAIT;
    END PROCESS;
END ARCHITECTURE arch;
-- Testbech ends here.
  