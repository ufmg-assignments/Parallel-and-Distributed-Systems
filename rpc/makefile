stubs:
	@if [ ! -f diretorio_pb2.py ] || [ ! -f diretorio_pb2_grpc.py ] || [ ! -f integracao_pb2.py ] || [ ! -f integracao_pb2_grpc.py ]; then \
		echo "python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. diretorio.proto"; \
		python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. diretorio.proto; \
		echo "python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. integracao.proto"; \
		python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. integracao.proto; \
	fi

clean:
	rm -f diretorio_pb2.py diretorio_pb2_grpc.py
	rm -f integracao_pb2.py integracao_pb2_grpc.py

run_cli_dir: stubs
	python3 cln_dir.py $(arg)

run_serv_dir: stubs
	python3 srv_dir.py $(arg)

run_cli_int: stubs
	python3 cln_int.py $(arg)

run_serv_int: stubs
	python3 srv_int.py $(arg)
