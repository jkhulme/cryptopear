class NameSpoofer

  def random_name
    [random_first_name, random_last_name].join(' ')
  end

  def random_first_name
    pool= %w{walter jesse james jack wolf terrence
    tom billy bartholomew hugh stepher lynne lisa alice
    william bob mary ryan paul daniel clarence margret}
    pool.sample.capitalize
  end

  def random_last_name
    pool = %w{heisenberg white smith willis jones crump
    pennywinkle bucket shraeder king wheatley fraser
    lannister harris hulme brown maverick}
    pool.sample.capitalize
  end

end

