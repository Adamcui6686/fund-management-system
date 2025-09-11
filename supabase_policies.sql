-- 禁用行级安全策略（RLS）以允许匿名访问
-- 注意：这仅适用于内部系统，不适合公开应用

-- 禁用所有表的RLS
ALTER TABLE strategies DISABLE ROW LEVEL SECURITY;
ALTER TABLE nav_records DISABLE ROW LEVEL SECURITY;
ALTER TABLE investors DISABLE ROW LEVEL SECURITY;
ALTER TABLE products DISABLE ROW LEVEL SECURITY;
ALTER TABLE product_strategy_weights DISABLE ROW LEVEL SECURITY;
ALTER TABLE investments DISABLE ROW LEVEL SECURITY;

-- 或者，如果要启用RLS，可以创建允许所有操作的策略
-- 对于内部私募基金系统，这样设置比较简单

-- CREATE POLICY "Allow all operations on strategies" ON strategies
-- FOR ALL USING (true) WITH CHECK (true);

-- CREATE POLICY "Allow all operations on nav_records" ON nav_records
-- FOR ALL USING (true) WITH CHECK (true);

-- CREATE POLICY "Allow all operations on investors" ON investors
-- FOR ALL USING (true) WITH CHECK (true);

-- CREATE POLICY "Allow all operations on products" ON products
-- FOR ALL USING (true) WITH CHECK (true);

-- CREATE POLICY "Allow all operations on product_strategy_weights" ON product_strategy_weights
-- FOR ALL USING (true) WITH CHECK (true);

-- CREATE POLICY "Allow all operations on investments" ON investments
-- FOR ALL USING (true) WITH CHECK (true);

