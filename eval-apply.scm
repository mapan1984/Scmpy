(load "representation.scm")
(load "environment.scm")

;;;;;;;;;;; apply
;; apply求值: 将procedure应用于arguments
;; arg:
;;   procedure
;;   arguments
(define (apply procedure arguments)
  (cond ((primitive-procedure? procedure)  ;; 基本过程
         (apply-primitive-procedure procedure arguments))
        ((compound-procedure? procedure)  ;; 复合过程，顺序地求值组成该过程体的那些表达式
         (eval-sequence
           (procedure-body procedure) ;表达式序列
           (extend-environment
             (procedure-parameters procedure)
             arguments
             (procedure-environment procedure))))
        (else
          (error "Unknown procedure type -- APPLY" procedure))))

;;;;;;;;;;; eval
;; eval解释器: 求值表达式
;; arg: 
;;   exp 表达式
;;   env 环境
(define (eval exp env)
  (cond ((self-evaluating? exp) exp)  ;; 自解释表达式，直接返回表达式
        ((variable? exp) (lookup-variable-value exp env))  ;; 变量，在环境中找出值
        ((quoted? exp) (text-of-quotation exp))  ;; 'quote，返回被引的表达式
        ((assignment? exp) (eval-assignment exp env))  ;; 赋值，递归的调用eval去计算出需要关联与这个变量的新值，而后修改环境
        ((definition? exp) (eval-definition exp env))  ;; 定义
        ((if? exp) (eval-if exp env))  ;; if语句，在谓词为真时求值其推论部分，否则求值其替代部分
        ((lambda? exp)  ;; lambda表达式，转换为一个可以应用的过程
         (make-procedure (lambda-parameters exp)
                         (lambda-body exp)
                         env))
        ((begin? exp)  ;; begin表达式，按顺序求值出现的一系列表达式
         (eval-sequence (begin-actions exp) env))
        ((cond? exp) (eval (cond->if exp) env))  ;; cond表达式，将其变换为一组嵌套的if表达式
        ((application? exp)  ;; 过程应用，递归地求值组合式的运算符部分和运算对象部分，而后将这样得到的过程和参数送给apply，由它去处理实际的过程应用
         (apply (eval (operator exp) env)
                (list-of-values (operands exp) env)))
        (else
          (error "Unknown expression type -- EVAL" exp))))

;;;;;;;;;; 过程参数
;; list-of-values: 以组合式的运算对象为参数，求值各个运算对象，返回这些值的表
;; arg:
;;   exps: 组合式的运算对象
;;   env: 环境
;; return:
;;   求值各个运算对象，返回这些值的表
(define (list-of-values exps env)
  (if (no-operands? exps)
      '()
      (cons (eval (first-operand exps) env)
            (list-of-values (rest-operands exps) env))))

;;;;;;;;;;; 条件
;; eval-if: 在给定环境判断if表达是的谓词是否为真，为真求值这个if的推论部分，
;;                                                为假求值这个if的替代部分
(define (eval-if exp env)
  (if (true? (eval (if-predicate exp) env))
      (eval (if-consequent exp) env)
      (eval (if-alternative exp) env)))

;;;;;;;;;; 序列
;; eval-sequence: 依次对表达式序列中的表达式求值
;; arg:
;;   exps: 表达式序列
;;   env: 环境
;; return:
;;   最后一个表达式的值
(define (eval-sequence exps env)
  (cond ((last-exp? exps) (eval (first-exp exps) env))
        (else (eval (first-exp exps) env)
              (eval-sequence (rest-exps exps) env))))

;;;;;;;;;; 赋值与定义
;; eval-assignment: 找出exp中的变量和需要赋的值，
;;                  将变量与值安置到指定环境中
(define (eval-assignment exp env)
  (set-variable-value! (assignment-variable exp)
                       (eval (assignment-value exp) env)
                       env)
  'ok)

;; eval-definition: 找出exp中的变量和需要赋的值，
;;                  将变量与值安置到指定环境中
(define (eval-definition exp env)
  (define-variable! (definition-variable exp)
                    (eval (definition-value exp) env)
                    env)
  'ok)
