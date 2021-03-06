library ieee;
use ieee.std_logic_1164.all;

library ahir;
use ahir.mem_function_pack.all;
use ahir.merge_functions.all;
use ahir.mem_component_pack.all;

entity Mem_Test_Block is
  generic(data_width, addr_width,tag_width, block_id, iteration_count : natural := 0);
  port(lr_addr: out std_logic_vector(addr_width-1 downto 0);
       lr_tag : out std_logic_vector(tag_width-1 downto 0);
       lr_req : out std_logic;
       lr_ack : in std_logic;
       lc_req : out std_logic;
       lc_ack : in std_logic;
       lc_data : in std_logic_vector(data_width-1 downto 0);
       lc_tag : in  std_logic_vector(tag_width-1 downto 0);
       sr_addr: out std_logic_vector(addr_width-1 downto 0);
       sr_data : out std_logic_vector(data_width-1 downto 0);
       sr_tag : out std_logic_vector(tag_width-1 downto 0);
       sr_req : out std_logic;
       sr_ack : in std_logic;
       sc_req : out std_logic;
       sc_ack : in std_logic;
       sc_tag : in  std_logic_vector(tag_width-1 downto 0);
       clock, reset  : in std_logic);
end entity;


architecture behave of Mem_Test_Block is
  -- purpose: catch U/X
  function Is01 (
    constant x : std_logic_vector)
    return boolean is
    alias lx : std_logic_vector(1 to x'length) is x;
    variable ret_var : boolean;
  begin  -- Is01
    ret_var := true;
    for I  in 1 to x'length loop
      if(lx(I) /= '0' and lx(I) /= '1') then
        ret_var := false;
        exit;
      end if;
    end loop;  -- I 
    return(ret_var);
  end Is01;

  signal Lsig : natural;
begin  -- behave

  -- request process
  process
    constant tag : std_logic_vector(tag_width-1 downto 0) := Natural_To_SLV(block_id,tag_width);
  begin
    sr_req <= '0';
    lr_req <= '0';
    sr_addr <= (others => '0');
    lr_addr <= (others => '0');
    sr_data <= (others => '0');
    sr_tag <= (others => '0');
    lr_tag <= (others => '0');

    wait on reset until reset = '0';
    for I in 0 to iteration_count - 1 loop
      wait on clock until clock = '1';
      wait for 1 ns;
      sr_addr <= Natural_To_SLV(I,addr_width-tag_width) & tag;
      sr_data <= Natural_To_SLV(I+block_id,data_width);
      sr_tag <= tag;
      sr_req <= '1';
      while(sr_ack /= '1') loop
        wait on clock until clock = '1';
      end loop;
      sr_req <= '0';
      lr_addr <= Natural_To_SLV(I,addr_width-tag_width) & tag;
      lr_tag <= Natural_To_SLV(I,tag_width);
      lr_tag  <= tag;
      lr_req <= '1';
      while(lr_ack /= '1') loop
        wait on clock until clock = '1';
      end loop;
      wait for 1 ns;
      lr_req <= '0';
    end loop;  -- I
    assert false report "Test Over in Block " & Convert_To_String(block_id) severity note;
    wait;
  end process;

  -- complete process
  process
    variable L : natural := block_id;
    variable dval : std_logic_vector(1 to data_width);
  begin
    Lsig <= L;
    lc_req <= '1';
    wait on reset until reset = '0';
    while true loop
      wait on clock until clock = '1';
      if(lc_ack = '1') then
        dval := Natural_To_SLV(L,data_width);
        assert (lc_data = dval) report "LOAD ERROR: expected= " & Convert_To_String(dval) & " actual= "
          & Convert_To_String(lc_data)  severity error;
      
        assert Is01(lc_data) report "LOAD ERROR: U/X seen in output " severity error;
        L := L + 1;
        Lsig <= L;
      end if;
    end loop;
  end process;

  sc_req <= '1';
  
end behave;
