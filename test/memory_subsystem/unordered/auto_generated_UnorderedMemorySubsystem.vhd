
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

ENTITY tb_UnorderedMemorySubsystem IS END;
ARCHITECTURE arch OF tb_UnorderedMemorySubsystem IS 

    ----------------------------------------------------------------
    -- Component declaration.
    ----------------------------------------------------------------
    COMPONENT UnorderedMemorySubsystem 
    PORT ( 
        lr_addr_in : in std_logic_vector((num_loads*addr_width)-1 downto 0);
        lr_req_in : in std_logic_vector(num_loads-1 downto 0);
        lr_ack_out : out std_logic_vector(num_loads-1 downto 0);
        lr_tag_in : in std_logic_vector((num_loads*tag_width)-1 downto 0);
        lc_data_out : out std_logic_vector((num_loads*data_width)-1 downto 0);
        lc_req_in : in std_logic_vector(num_loads-1 downto 0);
        lc_ack_out : out std_logic_vector(num_loads-1 downto 0);
        lc_tag_out : out std_logic_vector((num_loads*tag_width)-1 downto 0);
        sr_addr_in : in std_logic_vector((num_stores*addr_width)-1 downto 0);
        sr_data_in : in std_logic_vector((num_stores*data_width)-1 downto 0);
        sr_req_in : in std_logic_vector(num_stores-1 downto 0);
        sr_ack_out : out std_logic_vector(num_stores-1 downto 0);
        sr_tag_in : in std_logic_vector((num_stores*tag_width)-1 downto 0);
        sc_req_in : in std_logic_vector(num_stores-1 downto 0);
        sc_ack_out : out std_logic_vector(num_stores-1 downto 0);
        sc_tag_out : out std_logic_vector((num_stores*tag_width)-1 downto 0);
        clock : in std_logic;
        reset : in std_logic
    );
    END COMPONENT;
    
    -- Signals in entity 
    SIGNAL lr_addr_in :  std_logic_vector((num_loads*addr_width)-1 downto 0);
    SIGNAL lr_req_in :  std_logic_vector(num_loads-1 downto 0);
    SIGNAL lr_ack_out :  std_logic_vector(num_loads-1 downto 0);
    SIGNAL lr_tag_in :  std_logic_vector((num_loads*tag_width)-1 downto 0);
    SIGNAL lc_data_out :  std_logic_vector((num_loads*data_width)-1 downto 0);
    SIGNAL lc_req_in :  std_logic_vector(num_loads-1 downto 0);
    SIGNAL lc_ack_out :  std_logic_vector(num_loads-1 downto 0);
    SIGNAL lc_tag_out :  std_logic_vector((num_loads*tag_width)-1 downto 0);
    SIGNAL sr_addr_in :  std_logic_vector((num_stores*addr_width)-1 downto 0);
    SIGNAL sr_data_in :  std_logic_vector((num_stores*data_width)-1 downto 0);
    SIGNAL sr_req_in :  std_logic_vector(num_stores-1 downto 0);
    SIGNAL sr_ack_out :  std_logic_vector(num_stores-1 downto 0);
    SIGNAL sr_tag_in :  std_logic_vector((num_stores*tag_width)-1 downto 0);
    SIGNAL sc_req_in :  std_logic_vector(num_stores-1 downto 0);
    SIGNAL sc_ack_out :  std_logic_vector(num_stores-1 downto 0);
    SIGNAL sc_tag_out :  std_logic_vector((num_stores*tag_width)-1 downto 0);
    SIGNAL clock :  std_logic;
    SIGNAL reset :  std_logic;

BEGIN
    -- Instantiate a dut 
    dut : UnorderedMemorySubsystem PORT MAP( 
        lr_addr_in => lr_addr_in,
        lr_req_in => lr_req_in,
        lr_ack_out => lr_ack_out,
        lr_tag_in => lr_tag_in,
        lc_data_out => lc_data_out,
        lc_req_in => lc_req_in,
        lc_ack_out => lc_ack_out,
        lc_tag_out => lc_tag_out,
        sr_addr_in => sr_addr_in,
        sr_data_in => sr_data_in,
        sr_req_in => sr_req_in,
        sr_ack_out => sr_ack_out,
        sr_tag_in => sr_tag_in,
        sc_req_in => sc_req_in,
        sc_ack_out => sc_ack_out,
        sc_tag_out => sc_tag_out,
        clock => clock,
        reset => reset);
    test : PROCESS 
        -- Declare variables to store the values stored in test files. 
        VARIABLE tmp_lr_addr_in :  std_logic_vector((num_loads*addr_width)-1 downto 0);
        VARIABLE tmp_lr_req_in :  std_logic_vector(num_loads-1 downto 0);
        VARIABLE tmp_lr_ack_out :  std_logic_vector(num_loads-1 downto 0);
        VARIABLE tmp_lr_tag_in :  std_logic_vector((num_loads*tag_width)-1 downto 0);
        VARIABLE tmp_lc_data_out :  std_logic_vector((num_loads*data_width)-1 downto 0);
        VARIABLE tmp_lc_req_in :  std_logic_vector(num_loads-1 downto 0);
        VARIABLE tmp_lc_ack_out :  std_logic_vector(num_loads-1 downto 0);
        VARIABLE tmp_lc_tag_out :  std_logic_vector((num_loads*tag_width)-1 downto 0);
        VARIABLE tmp_sr_addr_in :  std_logic_vector((num_stores*addr_width)-1 downto 0);
        VARIABLE tmp_sr_data_in :  std_logic_vector((num_stores*data_width)-1 downto 0);
        VARIABLE tmp_sr_req_in :  std_logic_vector(num_stores-1 downto 0);
        VARIABLE tmp_sr_ack_out :  std_logic_vector(num_stores-1 downto 0);
        VARIABLE tmp_sr_tag_in :  std_logic_vector((num_stores*tag_width)-1 downto 0);
        VARIABLE tmp_sc_req_in :  std_logic_vector(num_stores-1 downto 0);
        VARIABLE tmp_sc_ack_out :  std_logic_vector(num_stores-1 downto 0);
        VARIABLE tmp_sc_tag_out :  std_logic_vector((num_stores*tag_width)-1 downto 0);
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
            -- read lr_addr_in value
            read(l, tmp_lr_addr_in, good_val);
            assert good_val REPORT "bad lr_addr_in value";
            read(l, space); -- skip a space

            -- read lr_req_in value
            read(l, tmp_lr_req_in, good_val);
            assert good_val REPORT "bad lr_req_in value";
            read(l, space); -- skip a space

            -- read lr_ack_out value
            read(l, tmp_lr_ack_out, good_val);
            assert good_val REPORT "bad lr_ack_out value";
            assert tmp_lr_ack_out = lr_ack_out REPORT "vector mismatch";            read(l, space); -- skip a space

            -- read lr_tag_in value
            read(l, tmp_lr_tag_in, good_val);
            assert good_val REPORT "bad lr_tag_in value";
            read(l, space); -- skip a space

            -- read lc_data_out value
            read(l, tmp_lc_data_out, good_val);
            assert good_val REPORT "bad lc_data_out value";
            assert tmp_lc_data_out = lc_data_out REPORT "vector mismatch";            read(l, space); -- skip a space

            -- read lc_req_in value
            read(l, tmp_lc_req_in, good_val);
            assert good_val REPORT "bad lc_req_in value";
            read(l, space); -- skip a space

            -- read lc_ack_out value
            read(l, tmp_lc_ack_out, good_val);
            assert good_val REPORT "bad lc_ack_out value";
            assert tmp_lc_ack_out = lc_ack_out REPORT "vector mismatch";            read(l, space); -- skip a space

            -- read lc_tag_out value
            read(l, tmp_lc_tag_out, good_val);
            assert good_val REPORT "bad lc_tag_out value";
            assert tmp_lc_tag_out = lc_tag_out REPORT "vector mismatch";            read(l, space); -- skip a space

            -- read sr_addr_in value
            read(l, tmp_sr_addr_in, good_val);
            assert good_val REPORT "bad sr_addr_in value";
            read(l, space); -- skip a space

            -- read sr_data_in value
            read(l, tmp_sr_data_in, good_val);
            assert good_val REPORT "bad sr_data_in value";
            read(l, space); -- skip a space

            -- read sr_req_in value
            read(l, tmp_sr_req_in, good_val);
            assert good_val REPORT "bad sr_req_in value";
            read(l, space); -- skip a space

            -- read sr_ack_out value
            read(l, tmp_sr_ack_out, good_val);
            assert good_val REPORT "bad sr_ack_out value";
            assert tmp_sr_ack_out = sr_ack_out REPORT "vector mismatch";            read(l, space); -- skip a space

            -- read sr_tag_in value
            read(l, tmp_sr_tag_in, good_val);
            assert good_val REPORT "bad sr_tag_in value";
            read(l, space); -- skip a space

            -- read sc_req_in value
            read(l, tmp_sc_req_in, good_val);
            assert good_val REPORT "bad sc_req_in value";
            read(l, space); -- skip a space

            -- read sc_ack_out value
            read(l, tmp_sc_ack_out, good_val);
            assert good_val REPORT "bad sc_ack_out value";
            assert tmp_sc_ack_out = sc_ack_out REPORT "vector mismatch";            read(l, space); -- skip a space

            -- read sc_tag_out value
            read(l, tmp_sc_tag_out, good_val);
            assert good_val REPORT "bad sc_tag_out value";
            assert tmp_sc_tag_out = sc_tag_out REPORT "vector mismatch";            read(l, space); -- skip a space

            -- read clock value
            read(l, tmp_clock, good_val);
            assert good_val REPORT "bad clock value";
            read(l, space); -- skip a space

            -- read reset value
            read(l, tmp_reset, good_val);
            assert good_val REPORT "bad reset value";
            read(l, space); -- skip a space


            -- Assign temp signals to ports 
            lr_addr_in <= tmp_lr_addr_in;
            lr_req_in <= tmp_lr_req_in;
            lr_ack_out <= tmp_lr_ack_out;
            lr_tag_in <= tmp_lr_tag_in;
            lc_data_out <= tmp_lc_data_out;
            lc_req_in <= tmp_lc_req_in;
            lc_ack_out <= tmp_lc_ack_out;
            lc_tag_out <= tmp_lc_tag_out;
            sr_addr_in <= tmp_sr_addr_in;
            sr_data_in <= tmp_sr_data_in;
            sr_req_in <= tmp_sr_req_in;
            sr_ack_out <= tmp_sr_ack_out;
            sr_tag_in <= tmp_sr_tag_in;
            sc_req_in <= tmp_sc_req_in;
            sc_ack_out <= tmp_sc_ack_out;
            sc_tag_out <= tmp_sc_tag_out;
            clock <= tmp_clock;
            reset <= tmp_reset;

        END LOOP;
        ASSERT false REPORT "Test complete";
        WAIT;
    END PROCESS;
END ARCHITECTURE arch;
-- Testbech ends here.
  